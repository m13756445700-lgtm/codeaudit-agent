"""Evidence quality only. This module contains no vulnerability detection rules."""
import copy
from agent.v2.repository import safe_path, digest


def validate(finding, repo, metadata, receipts, knowledge):
    result = copy.deepcopy(finding)
    problems = []
    for key in ('id', 'title', 'category', 'reasoning_summary', 'false_positive_analysis', 'remediation',
                'severity', 'confidence', 'sanitizer_analysis', 'reachability',
                'controllability', 'security_boundary', 'confidence_rationale'):
        if not isinstance(result.get(key), str) or not result[key].strip():
            problems.append('missing:' + key)
    if result.get('status') not in ('CONFIRMED', 'LIKELY', 'INSUFFICIENT_EVIDENCE', 'REJECTED'):
        problems.append('invalid status')
    for key in ('exploit_preconditions', 'unknowns'):
        value = result.get(key)
        if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
            problems.append('invalid:' + key)
    counter = result.get('counter_evidence')
    if not isinstance(counter, list):
        problems.append('invalid:counter_evidence')
        counter = []
    flow = result.get('data_flow')
    if not isinstance(flow, list) or not flow:
        problems.append('missing data flow')
        flow = []
    references = [('source', result.get('source')), *[(f'data_flow[{i}]', ref) for i, ref in enumerate(flow)],
                  ('sink', result.get('sink')), *[(f'counter_evidence[{i}]', ref) for i, ref in enumerate(counter)]]
    hashes = {}
    for location, ref in references:
        try:
            if not isinstance(ref, dict):
                raise ValueError('missing reference')
            path, line, quote, symbol = ref['file'], ref['line'], ref['evidence'], ref['symbol']
            if type(line) is not int or line < 1 or not isinstance(quote, str) or not quote.strip() or not symbol:
                raise ValueError('invalid reference')
            p = safe_path(repo, path)
            current = digest(p)
            if metadata['files'].get(path) != current:
                raise ValueError('snapshot changed')
            lines = p.read_text(errors='replace').splitlines()
            if line > len(lines) or quote.strip() not in lines[line-1]:
                raise ValueError('quote not at cited line')
            if symbol not in '\n'.join(lines):
                raise ValueError('symbol absent')
            if not any(r['file'] == path and r['sha256'] == current and r['start'] <= line <= r['end'] for r in receipts):
                raise ValueError('source was not read through tool')
            hashes[path] = current
        except (KeyError, ValueError, OSError, TypeError) as error:
            problems.append('reference:' + location + ':' + str(error))
    used = result.get('knowledge_used', [])
    if not isinstance(used, list) or any(item not in knowledge for item in used):
        problems.append('knowledge citation not retrieved')
    # Cannot promote a model verdict or semantically overrule it.
    result['ai_status'] = result.get('status')
    if problems:
        result['status'] = 'INSUFFICIENT_EVIDENCE'
    result['evidence_gate'] = {'passed': not problems, 'problems': problems,
                               'snapshot_sha256': metadata['snapshot_sha256'], 'files': hashes,
                               'scope': 'reference integrity and completeness; AI owns security judgment'}
    return result
