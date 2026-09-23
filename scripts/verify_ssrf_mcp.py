"""Actual SQL/Command compatibility and SSRF MCP verification; no target HTTP calls."""
import json
import runpy
from pathlib import Path

root = Path(__file__).resolve().parents[1]
transport = runpy.run_path(str(root / 'scripts/verify_command_mcp.py'))
call = transport['call']
output = root / 'runs/phase8-ssrf'
output.mkdir(parents=True, exist_ok=True)
call.__globals__['OUT'] = output
call.__globals__['records'] = []
manifest = call('InventoryRepository', {'repository': 'ssrf-lab'})
request = {'repository': 'ssrf-lab', 'commit': manifest['commit']}
scanned = call('ScanCandidates', request)
candidates = [c for c in scanned['candidates'] if c['category'] == 'SSRF']
assert {c['line'] for c in candidates} == {13,18,23}
findings = []
for c in candidates:
    point = dict(request, file=c['file'], line=c['line'])
    call('ReadCodeSlice', point)
    call('HashEvidence', point)
    finding = call('RunValidation', point)
    assert finding['category'] == 'SSRF'
    assert finding['status'] == {13:'VERIFIED',18:'REJECTED',23:'NEEDS_REVIEW'}[c['line']]
    assert finding['evidence_integrity']['status'] == 'PASS'
    findings.append(finding)
(output / 'mcp-result.json').write_text(json.dumps({'passed':True,'repository':request,
    'checks':call.__globals__['records'],'findings':findings},indent=2))
print('SSRF MCP: 3/3 verdicts PASS')
