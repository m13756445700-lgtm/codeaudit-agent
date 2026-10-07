"""Evidence quality only. This module contains no vulnerability detection rules."""
import copy
import json
import re
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
    scope = result.get('judgment_scope')
    exposure = result.get('deployment_exposure')
    if scope not in ('conditional_code', 'deployment'):
        problems.append('invalid:judgment_scope')
    if exposure not in ('unknown', 'evidenced', 'not_evidenced'):
        problems.append('invalid:deployment_exposure')
    if exposure == 'evidenced' and not any(
            isinstance(a, dict) and a.get('state') == 'verified' and a.get('references')
            for a in (result.get('environment_assumptions') if isinstance(result.get('environment_assumptions'), list) else [])):
        problems.append('deployment exposure requires verified environment evidence')
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
    implementation_locations = set()
    if result.get('status') == 'REJECTED':
        if not counter:
            problems.append('REJECTED requires implementation counter_evidence')
        implementation_locations.update(f'counter_evidence[{i}]' for i in range(len(counter)))
    for field in ('defense_claims', 'environment_assumptions'):
        claims = result.get(field)
        if not isinstance(claims, list) or len(claims) > 16:
            problems.append('invalid:' + field)
            continue
        for i, claim in enumerate(claims):
            location = f'{field}[{i}]'
            if not isinstance(claim, dict) or not isinstance(claim.get('claim'), str) or not claim['claim'].strip():
                problems.append('invalid:' + location)
                continue
            refs = claim.get('references')
            if not isinstance(refs, list) or len(refs) > 16:
                problems.append('invalid references:' + location)
                continue
            if field == 'defense_claims':
                if not refs or not isinstance(claim.get('limitations'), str):
                    problems.append('defense requires implementation references and limitations:' + location)
            else:
                state = claim.get('state')
                if state not in ('verified', 'unknown') or type(claim.get('affects_verdict')) is not bool:
                    problems.append('invalid assumption:' + location)
                if state == 'verified' and not refs:
                    problems.append('verified assumption requires evidence:' + location)
                if state == 'unknown' and claim.get('affects_verdict') and result.get('status') != 'INSUFFICIENT_EVIDENCE':
                    if scope != 'conditional_code':
                        problems.append('unresolved environment affects verdict:' + location)
                    elif not isinstance(result.get('exploit_preconditions'), list) or claim['claim'] not in result['exploit_preconditions']:
                        problems.append('conditional verdict must retain material unknown as explicit precondition:' + location
                                        + '; add its claim as a separate, exactly equal exploit_preconditions item (no prefix or paraphrase): '
                                        + json.dumps(claim['claim'], ensure_ascii=False))
                    if exposure != 'unknown':
                        problems.append('unknown material environment cannot establish deployment exposure:' + location)
            for j, ref in enumerate(refs):
                ref_location = f'{location}.references[{j}]'
                references.append((ref_location, ref))
                if field == 'defense_claims':
                    implementation_locations.add(ref_location)
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
            # A provenance check, not a proof that the claimed defense is effective.
            # Imports/declarations of dependencies alone are not implementation evidence.
            if location in implementation_locations and re.match(
                    r'^\s*(?:from\s+\S+\s+import\b|import\b|#\s*include\b|using\s+\S+\s*;)', lines[line-1]):
                raise ValueError('dependency import is not implementation evidence')
            if location in implementation_locations and re.match(
                    r'^\s*(?:(?:async\s+)?def\s+|class\s+).*?(?:[:(])\s*$', lines[line-1]):
                raise ValueError('definition header alone is not implementation behavior evidence')
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
