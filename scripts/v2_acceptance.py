"""Real model/OctoBus acceptance. No mocked model, no ground-truth in model context."""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent.v2.repository import snapshot, profile
from agent.v2.tools import ToolLayer
from agent.v2.transport import OctoBus
from agent.v2.engine import Engine
from agent.v2.model import Model
from agent.v2.static_baseline import evaluate as static_evaluate


def audit(case):
    workspaces = Path(os.environ.get('CODEAUDIT_WORKSPACES', '/tmp/codeaudit-v2/workspaces'))
    directory, metadata = snapshot(ROOT / 'benchmark' / case['id'], workspaces)
    transport = OctoBus(os.environ['CODEAUDIT_MCP_URL'], os.environ['CODEAUDIT_OCTOBUS_TOKEN'], directory.name)
    engine = Engine(Model(), transport, directory, metadata, profile(directory / 'repo'))
    summary = engine.run()
    # Same committed rules, same immutable snapshot. Static run is independent of model tool choices.
    static = transport.call('static.semgrep', {})
    findings = json.loads((directory / 'findings.json').read_text())
    record = {'case': case['id'], 'audit_id': directory.name, 'run_status': summary['status'],
              'snapshot_sha256': metadata['snapshot_sha256'], 'expected': case, 'findings': findings,
              'static_signals': static['signals'], 'static_analysis': static_evaluate(directory / 'repo', metadata, static['signals']), 'plan': engine.plan, 'calls': summary['tool_calls']}
    print(case['id'], summary['status'], [f['status'] for f in findings], 'static signals:', len(static['signals']), flush=True)
    return record


def matches(f, case):
    # Match location and category, not mere presence of any positive finding.
    return (f.get('category', '').lower().replace(' ', '_') == case['category'] and
            f.get('sink', {}).get('file') == case['file'] and case['sink'] in f.get('sink', {}).get('evidence', ''))


def metrics(records):
    tp = fp = fn = rejected = ai_only = cross = complete = 0
    positives = 0
    for r in records:
        expected = r['expected']
        confirmed = [f for f in r['findings'] if f['status'] == 'CONFIRMED']
        matching = [f for f in confirmed if matches(f, expected)]
        if expected['status'] == 'CONFIRMED':
            tp += bool(matching)
            fn += not bool(matching)
            fp += len(confirmed) - bool(matching)
        else:
            fp += len(confirmed)
        positives += len(confirmed)
        complete += sum(f['evidence_gate']['passed'] for f in confirmed)
        if matching and not r['static_signals']:
            ai_only += 1
        if matching and len({v['file'] for v in [matching[0]['source'], *matching[0]['data_flow'], matching[0]['sink']]}) > 1:
            cross += 1
        rejected += bool(r['static_signals'] and any(f['status'] == 'REJECTED' and matches(f, expected) for f in r['findings']))
    precision = tp/(tp+fp) if tp+fp else 0
    recall = tp/(tp+fn) if tp+fn else 0
    return {'true_positive': tp, 'false_positive': fp, 'false_negative': fn, 'precision': precision,
            'recall': recall, 'f1': 2*precision*recall/(precision+recall) if precision+recall else 0,
            'evidence_completeness': complete/positives if positives else None, 'cross_file_detection': cross,
            'ai_only_detection': ai_only, 'ai_fp_rejection': rejected}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['integration', 'benchmark', 'ablation'])
    parser.add_argument('--reuse', type=Path, help='Explicit evidence replay; default always performs fresh model calls')
    parser.add_argument('--refresh-static', action='store_true', help='Re-evaluate preserved static signals on original snapshots; requires --reuse; no new LLM calls')
    args = parser.parse_args()
    if args.refresh_static and not args.reuse:
        parser.error('--refresh-static requires --reuse')
    cases = json.loads((ROOT/'benchmark/ground_truth.json').read_text())
    if args.mode != 'benchmark':
        cases = cases[:2]
    if args.reuse:
        records = json.loads(args.reuse.read_text())['records']
        if args.refresh_static:
            for record in records:
                directory = Path(os.environ['CODEAUDIT_WORKSPACES']) / record['audit_id']
                metadata = json.loads((directory/'metadata.json').read_text())
                if metadata['snapshot_sha256'] != record['snapshot_sha256']:
                    raise ValueError('Replay snapshot differs')
                record['static_analysis'] = static_evaluate(directory/'repo', metadata, record['static_signals'])
    else:
        records = []
        for case in cases:
            records.append(audit(case))
            out = ROOT/'runs/v2'
            out.mkdir(parents=True, exist_ok=True)
            (out/(args.mode+'-partial.json')).write_text(json.dumps({'records': records}, indent=2))
    scores = metrics(records)
    checks = {'runs_complete': all(r['run_status']=='COMPLETE' for r in records),
              'no_false_positives': scores['false_positive']==0,
              'all_expected_detected': scores['false_negative']==0,
              'ground_truth_count': len(records)==len(cases),
              'real_cross_file': scores['cross_file_detection'] >= 1,
              'ai_added_unruled': scores['ai_only_detection'] >= 1,
              'ai_rejected_static_fp': scores['ai_fp_rejection'] >= 1,
              'static_analysis_executed': all('static_analysis' in r and not r['static_analysis']['errors'] for r in records),
              'different_plans': len({json.dumps(r['plan'], sort_keys=True) for r in records}) > 1}
    rules = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'rules/semgrep').glob('*.yaml')}
    result = {'mode': args.mode, 'replay': bool(args.reuse), 'static_recomputed': args.refresh_static, 'passed': all(checks.values()), 'checks': checks,
              'metrics': scores, 'static_baseline': 'V1 committed Semgrep plus unchanged V1 analyzer/Gate on identical snapshot; scope remains Java/MyBatis',
              'static_only': {'llm_calls': 0, 'security_verdicts': sum(r.get('static_analysis', {}).get('security_verdicts', 0) for r in records),
                  'findings': [f for r in records for f in r.get('static_analysis', {}).get('findings', [])],
                  'candidate_count': sum(len(r['static_signals']) for r in records),
                  'verified_findings': sum(r.get('static_analysis', {}).get('confirmed', 0) for r in records),
                  'evaluation_errors': sum(len(r.get('static_analysis', {}).get('errors', [])) for r in records),
                  'verdict_comparison_available': all('static_analysis' in r for r in records),
                  'candidate_positive_cases': sum(bool(r['static_signals']) and r['expected']['status']=='CONFIRMED' for r in records),
                  'candidate_safe_cases': sum(bool(r['static_signals']) and r['expected']['status']=='SAFE' for r in records),
                  'unmatched_vulnerable_cases': sum(not r['static_signals'] and r['expected']['status']=='CONFIRMED' for r in records)},
              'rules_sha256': rules, 'records': records}
    out = ROOT/'runs/v2'
    out.mkdir(parents=True, exist_ok=True)
    (out/(args.mode+'.json')).write_text(json.dumps(result, indent=2))
    print(json.dumps({'passed':result['passed'], 'checks':checks, 'metrics':scores}, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
