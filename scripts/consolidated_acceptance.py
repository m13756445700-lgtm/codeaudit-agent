"""Freeze inputs offline; explicitly opt in to serial paid evaluation later.

Run as python -m scripts.consolidated_acceptance. Labels never enter model context.
This records evidence, not an automatic release approval or independent adjudication.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

from agent.v2.repository import snapshot, profile, files

ROOT = Path(__file__).resolve().parents[1]
CODE_DIRS = ('agent', 'knowledge', 'rules', 'scripts', 'schemas')


def hash_tree(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files(root)}


def implementation_hash():
    manifest = {name: hash_tree(ROOT/name) for name in CODE_DIRS}
    manifest['build'] = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                         for name in ('Dockerfile', 'pyproject.toml', 'docker-compose.yml', 'agent-compose.yml')}
    return hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()


def prepare(output, repeats=2, external=None):
    if output.exists():
        raise ValueError('Output exists; preserve previous attempts and choose a new directory')
    if not 1 <= repeats <= 5:
        raise ValueError('repeats must be1..5')
    cases = []
    for case in json.loads((ROOT/'benchmark/ground_truth.json').read_text()):
        cases.append({'id': case['id'], 'source': str(ROOT/'benchmark'/case['id']),
                      'kind': 'benchmark', 'target': case, 'policy': '', 'arms': ['on']})
    for case in json.loads((ROOT/'evaluation/business-ground-truth.json').read_text())['cases']:
        cases.append({'id': case['id'], 'source': str(ROOT/'evaluation'/case['source']),
                      'kind': 'business-development', 'target': case['target'],
                      'policy': case['policy'], 'arms': ['on', 'off', 'generic']})
    if external:
        extra = json.loads(external.read_text())
        for case in extra['cases']:
            if not case.get('provenance') or not case.get('target'):
                raise ValueError('External cases require provenance and predeclared target')
            cases.append({**case, 'source': str(Path(case['source']).resolve()),
                          'kind': 'external-predeclared', 'arms': ['on', 'off', 'generic']})
    if len({c['id'] for c in cases}) != len(cases):
        raise ValueError('Duplicate case IDs')
    jobs = []
    for case in cases:
        source = Path(case['source'])
        if not source.is_dir():
            raise ValueError('Source directory missing: ' + case['id'])
        case['source_hashes'] = hash_tree(source)
        for repeat in range(repeats):
            for arm in case['arms']:
                jobs.append({'case': case['id'], 'repeat': repeat, 'arm': arm})
    plan = {'schema': 1, 'implementation_sha256': implementation_hash(),
            'model': os.environ.get('CODEAUDIT_MODEL') or os.environ.get('LLM_MODEL') or 'deepseek-flash',
            'budget_per_run': {'max_iterations': 48, 'max_calls': 100, 'timeout': 1200},
            'cases': cases, 'jobs': jobs, 'repeats': repeats,
            'warning': 'Development cases are not blind evaluation. Completion and correctness are separate. Human adjudication required. No automatic publication.'}
    output.mkdir(parents=True)
    raw = json.dumps(plan, indent=2, sort_keys=True) + '\n'
    (output/'plan.json').write_text(raw)
    (output/'plan.sha256').write_text(hashlib.sha256(raw.encode()).hexdigest()+'\n')
    return plan


def load_frozen(output):
    raw = (output/'plan.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != (output/'plan.sha256').read_text().strip():
        raise ValueError('Frozen plan changed')
    plan = json.loads(raw)
    if implementation_hash() != plan['implementation_sha256']:
        raise ValueError('Implementation or knowledge changed; prepare a new evaluation')
    model = os.environ.get('CODEAUDIT_MODEL') or os.environ.get('LLM_MODEL') or 'deepseek-flash'
    if model != plan['model']:
        raise ValueError('Model differs from frozen plan')
    for case in plan['cases']:
        if hash_tree(Path(case['source'])) != case['source_hashes']:
            raise ValueError('Source changed: ' + case['id'])
    return plan


def run_live(output, max_runs):
    # Imports and credential use are intentionally confined to explicit live mode.
    from agent.v2.engine import Engine
    from agent.v2.model import Model
    from agent.v2.transport import OctoBus
    from scripts.knowledge_comparison import GenericKnowledge
    plan = load_frozen(output)
    results_path = output/'results.jsonl'
    records = [json.loads(line) for line in results_path.read_text().splitlines()] if results_path.exists() else []
    # A failed job is an attempt, never silently overwritten/retried in the same campaign.
    done = {r['job_index'] for r in records}
    cases = {c['id']: c for c in plan['cases']}
    count = 0
    for index, job in enumerate(plan['jobs']):
        if index in done:
            continue
        if count >= max_runs:
            break
        case = cases[job['case']]
        directory, metadata = snapshot(case['source'], Path(os.environ['CODEAUDIT_WORKSPACES']))
        transport = OctoBus(os.environ['CODEAUDIT_MCP_URL'], os.environ['CODEAUDIT_OCTOBUS_TOKEN'], directory.name)
        if job['arm'] == 'generic':
            transport = GenericKnowledge(transport)
        model = Model()
        engine = Engine(model, transport, directory, metadata, profile(directory/'repo'),
                        knowledge=job['arm'] != 'off', **plan['budget_per_run'])
        if case.get('policy'):
            engine.messages.append({'role': 'user', 'content': json.dumps({
                'operator_supplied_business_policy': case['policy'],
                'notice': 'Policy context only; verify implementation. Do not assume a vulnerability.'})})
        summary = engine.run()
        static = None
        if case['kind'] == 'benchmark' and not summary.get('failure'):
            from agent.v2.static_baseline import evaluate
            signals = transport.call('static.semgrep', {})
            static = evaluate(directory/'repo', metadata, signals['signals'])
        record = {'static_baseline': static, 'job_index': index, **job, 'summary': summary,
                  'findings': json.loads((directory/'findings.json').read_text()),
                  'adjudication': 'PENDING', 'implementation_sha256': plan['implementation_sha256']}
        with results_path.open('a') as handle:
            handle.write(json.dumps(record)+'\n')
            handle.flush()
            os.fsync(handle.fileno())
        count += 1
        print(json.dumps({'job': index, **job, 'status': summary['status'], 'failure': summary['failure']}), flush=True)
        if summary.get('failure') and 'Model HTTP error' in summary['failure']:
            (output/'STOPPED.json').write_text(json.dumps({'job': index, 'reason': summary['failure'],
                'instruction': 'Restore provider before another invocation. Failed attempt remains recorded.'}, indent=2))
            break
    return summarize(output)


def summarize(output):
    plan = json.loads((output/'plan.json').read_text())
    path = output/'results.jsonl'
    records = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
    # No binary pass based solely on status. A human must adjudicate target and extra findings.
    result = {'planned_runs': len(plan['jobs']), 'attempted_runs': len(records),
              'complete_runs': sum(r['summary']['status'] == 'COMPLETE' for r in records),
              'pending_runs': len(plan['jobs'])-len(records),
              'tokens_observed': sum(u.get('total_tokens', 0) for r in records for u in r['summary'].get('usage', [])),
              'release_ready': False, 'reason': 'Human correctness adjudication and independent acceptance required; completion alone is not correctness.'}
    (output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--live', action='store_true', help='Explicitly allow paid model calls against a previously frozen plan')
    parser.add_argument('--repeats', type=int, default=2)
    parser.add_argument('--external', type=Path)
    parser.add_argument('--max-runs', type=int, default=1, help='Per invocation paid-run cap; default1')
    args = parser.parse_args()
    if args.max_runs < 1:
        parser.error('max-runs must be positive')
    if args.live:
        print(json.dumps(run_live(args.output, args.max_runs), indent=2))
    else:
        plan = prepare(args.output, args.repeats, args.external)
        print(json.dumps({'mode': 'offline-preparation', 'planned_runs': len(plan['jobs']),
                          'model_calls': 0, 'implementation_sha256': plan['implementation_sha256']}, indent=2))


if __name__ == '__main__':
    main()
