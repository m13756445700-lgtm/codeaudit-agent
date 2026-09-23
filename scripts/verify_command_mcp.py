"""Verify SQL compatibility first, then real Command MCP calls. No model verdicts."""
import json
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
# Reuse the existing authenticated transport and all twelve Phase6 checks.
transport = runpy.run_path(str(root / 'scripts/verify_local_mcp.py'))
call = transport['call']
output = root / 'runs/phase8-command'
output.mkdir(parents=True, exist_ok=True)
call.__globals__['OUT'] = output
call.__globals__['records'] = []
manifest = call('InventoryRepository', {'repository': 'command-lab'})
request = {'repository': 'command-lab', 'commit': manifest['commit']}
scan = call('ScanCandidates', request)
commands = [c for c in scan['candidates'] if c['category'] == 'COMMAND_INJECTION']
assert {c['line'] for c in commands} == {12, 17, 22}
findings = []
for c in commands:
    point = dict(request, file=c['file'], line=c['line'])
    call('ReadCodeSlice', point)
    call('HashEvidence', point)
    finding = call('RunValidation', point)
    assert finding['status'] == {12: 'VERIFIED', 17: 'NEEDS_REVIEW', 22: 'REJECTED'}[c['line']]
    assert finding['category'] == 'COMMAND_INJECTION'
    assert finding['evidence_integrity']['status'] == 'PASS'
    findings.append(finding)
(output / 'mcp-result.json').write_text(json.dumps({'passed': True, 'repository': request,
    'checks': call.__globals__['records'], 'findings': findings}, indent=2))
print('Command MCP: 3/3 verdicts PASS')

# Optional fixture for the next bounded static-call implementation.
import sys
if '--static-flow' in sys.argv:
    call.__globals__['records'] = []
    manifest = call('InventoryRepository', {'repository': 'static-flow-lab'})
    request = {'repository': 'static-flow-lab', 'commit': manifest['commit']}
    scan = call('ScanCandidates', request)
    commands = [c for c in scan['candidates'] if c['category'] == 'COMMAND_INJECTION']
    assert len(commands) == 1
    point = dict(request, file=commands[0]['file'], line=commands[0]['line'])
    call('ReadCodeSlice', point)
    call('HashEvidence', point)
    result = call('RunValidation', point)
    assert result['status'] == 'VERIFIED'
    assert result['source']['file'].endswith('CommandEndpoint.java')
    assert result['sink']['file'].endswith('CommandRunner.java')
    assert any(r['type'] == 'STATIC_CALL_ARGUMENT' for r in result['dataflow'])
    (output / 'static-flow-mcp-result.json').write_text(json.dumps({'passed': True,
        'repository': request, 'finding': result, 'checks': call.__globals__['records']}, indent=2))
    print('Static cross-file Command MCP PASS')
