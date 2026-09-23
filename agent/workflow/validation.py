"""Accept model summaries only when equal to saved trusted validation results."""
import json
import re
from pathlib import Path

class OutputError(ValueError):
    pass


def verify_output(raw, trusted_runs):
    try:
        value = json.loads(raw)
        if set(value) != {'repository', 'commit', 'validation_run_ids', 'findings'}:
            raise ValueError('Unexpected output fields')
        ids, findings = value['validation_run_ids'], value['findings']
        if not isinstance(ids, list) or not isinstance(findings, list) or len(ids) != len(findings) or not ids or len(set(ids)) != len(ids):
            raise ValueError('Missing or duplicate validation results')
        for run_id, finding in zip(ids, findings):
            if not isinstance(run_id, str) or not re.fullmatch('[0-9a-f]{32}', run_id):
                raise ValueError('Invalid run identifier')
            record = json.loads((Path(trusted_runs)/run_id/'validation-result.json').read_text())
            if record['repository'] != value['repository'] or record['commit'] != value['commit'] or record['finding'] != finding:
                raise ValueError('Model result differs from trusted service result')
        return value
    except (ValueError, TypeError, KeyError, OSError) as exc:
        raise OutputError('UNTRUSTED_OR_INVALID_MODEL_OUTPUT') from exc


def structured_output(generate, trusted_runs, max_attempts=2):
    if not 1 <= max_attempts <= 3:
        raise ValueError('Retry limit must be 1..3')
    for attempt in range(max_attempts):
        try:
            return verify_output(generate(attempt), trusted_runs)
        except OutputError:
            pass
    raise OutputError('MODEL_OUTPUT_RETRIES_EXHAUSTED')


def verify_session(events, trusted_runs, repository, commit):
    """Verify host-collected Codex events, not model-provided transcript markers.

    The caller must supply events from the trusted runtime session directory.
    Coverage is bound to the scan and validation calls in this same session.
    """
    methods = {'inventory_repository', 'scan_candidates', 'read_code_slice', 'hash_evidence', 'run_validation'}
    calls = {m: [] for m in methods}
    final = None
    try:
        for event in events:
            if event.get('type') != 'event_msg':
                continue
            item = event['payload']
            if item.get('type') == 'task_complete':
                final = item.get('last_agent_message')
            if item.get('type') in {'exec_command_begin', 'exec_command_end', 'patch_apply_begin', 'patch_apply_end', 'web_search_begin', 'web_search_end'}:
                raise ValueError('Uncontrolled tool used')
            if item.get('type') != 'mcp_tool_call_end':
                continue
            invocation = item['invocation']
            tool = invocation['tool']
            method = tool.rsplit('__', 1)[-1]
            if invocation['server'] != 'octobus' or method not in methods:
                raise ValueError('Uncontrolled MCP method')
            arguments = invocation['arguments']
            request = json.loads(arguments.get('request_json', arguments.get('requestJson', '')))
            if request.get('repository') != repository or request.get('commit') != commit:
                raise ValueError('Request escaped audit scope')
            result = item['result']['Ok']
            if result.get('isError'):
                raise ValueError('Tool error')
            data = result.get('structuredContent')
            if data is None:
                data = json.loads(next(c['text'] for c in result['content'] if c['type'] == 'text'))
            data = json.loads(data['resultJson'])
            calls[method].append((request, data))
        if not calls['inventory_repository'] or len(calls['scan_candidates']) != 1:
            raise ValueError('Missing inventory or ambiguous scan')
        for _, data in calls['inventory_repository']:
            if data['result']['commit'] != commit:
                raise ValueError('Inventory commit differs')
        scan = calls['scan_candidates'][0][1]['result']
        if scan['commit'] != commit:
            raise ValueError('Scan commit differs')
        points = {(c['file'], c['line']) for c in scan['candidates']}
        for method in ('read_code_slice', 'hash_evidence', 'run_validation'):
            actual = {(r['file'], r['line']) for r, _ in calls[method]}
            if actual != points:
                raise ValueError('Candidate coverage differs')
        value = verify_output(final, trusted_runs)
        if value['repository'] != repository or value['commit'] != commit:
            raise ValueError('Final audit scope differs')
        executed = {data['run_id']: data['result'] for _, data in calls['run_validation']}
        if set(value['validation_run_ids']) != set(executed):
            raise ValueError('Missing or replayed validation IDs')
        for run_id, finding in zip(value['validation_run_ids'], value['findings']):
            if executed[run_id] != finding:
                raise ValueError('Final differs from actual tool response')
        return value
    except (ValueError, TypeError, KeyError, OSError, StopIteration) as exc:
        raise OutputError('SESSION_EVIDENCE_CHECK_FAILED') from exc
