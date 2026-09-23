"""Controlled service dispatcher. Repository identifiers resolve under one root."""
import json
import os
import sys
import uuid
from pathlib import Path
from agent.config import Config
from agent.preflight import inventory
from agent.scanner.semgrep import scan
from agent.evidence.model import reference, evidence_hash
from agent.analysis import analyze_candidate
from agent.report import finalize_finding, validate_finding
from agent.logging import event

ROOT = Path(__file__).resolve().parents[1]
METHODS = {'InventoryRepository', 'ScanCandidates', 'ReadCodeSlice', 'HashEvidence', 'RunValidation'}


def dispatch(method, request, config):
    if method not in METHODS or not isinstance(request, dict):
        raise ValueError('Unsupported method')
    allowed = {'repository', 'commit', 'file', 'line', 'end_line'}
    if set(request) - allowed:
        raise ValueError('Unexpected request fields')
    repo_id = request.get('repository')
    if not isinstance(repo_id, str) or not repo_id or Path(repo_id).is_absolute() or '..' in Path(repo_id).parts:
        raise ValueError('Invalid repository identifier')
    repo = config.repository(repo_id)
    manifest = inventory(repo, commit=request.get('commit'))
    if method != 'InventoryRepository' and not request.get('commit'):
        raise ValueError('Fixed commit required')
    run_id = uuid.uuid4().hex
    artifact_dir = config.output(run_id)
    event(artifact_dir / 'events.jsonl', run_id=run_id, method=method, status='STARTED')
    if method == 'InventoryRepository':
        result = {**manifest, 'repository': repo_id}
    elif method == 'ScanCandidates':
        result = {'candidates': scan(repo, ROOT / 'rules/semgrep', artifact_dir, timeout=config.command_timeout), 'commit': manifest['commit']}
    else:
        line = request.get('line')
        end = request.get('end_line', line)
        if type(line) is not int or type(end) is not int or end - line + 1 > config.max_slice_lines:
            raise ValueError('Invalid code slice range')
        ref = reference(repo, request['file'], line, end)
        if method == 'ReadCodeSlice':
            lines = (repo / ref['file']).read_text().splitlines()
            result = {'reference': ref, 'snippet': '\n'.join(lines[line-1:end]), 'commit': manifest['commit']}
        elif method == 'HashEvidence':
            result = {'reference': ref, 'commit': manifest['commit']}
        else:
            # Input identifies source bytes, never a user-supplied verdict.
            candidate = analyze_candidate(repo, {'file': ref['file'], 'line': line})
            result = finalize_finding(candidate, manifest, 'controlled-validation')
            validate_finding(result, ROOT / 'schemas/finding.schema.json')
            record = {'repository': repo_id, 'commit': manifest['commit'], 'finding': result}
            (artifact_dir / 'validation-result.json').write_text(json.dumps(record, ensure_ascii=False))
            (artifact_dir / 'validation-result.json').chmod(0o600)
    # A concurrent edit invalidates the entire response.
    inventory(repo, commit=manifest['commit'])
    event(artifact_dir / 'events.jsonl', run_id=run_id, method=method, finding_id=result.get('finding_id', ''), status='SUCCEEDED')
    return {'run_id': run_id, 'result': result}


def main():
    config = Config(Path(os.environ['CODEAUDIT_REPOSITORY_ROOT']), Path(os.environ['CODEAUDIT_OUTPUT_ROOT']))
    try:
        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536:
            raise ValueError('Request too large')
        payload = json.loads(raw)
        print(json.dumps(dispatch(payload['method'], payload['request'], config)))
    except Exception as exc:
        # Do not return raw exceptions containing paths, source or credentials.
        print(json.dumps({'error': type(exc).__name__, 'status': 'FAILED'}))
        raise SystemExit(1)

if __name__ == '__main__':
    main()
