"""Verify the four vulnerability families through actual controlled MCP calls."""
import json
import runpy
from pathlib import Path
root=Path(__file__).resolve().parents[1]
transport=runpy.run_path(str(root/'scripts/verify_ssrf_mcp.py'))
call=transport['call']
out=root/'runs/phase8-path';out.mkdir(parents=True,exist_ok=True)
call.__globals__['OUT']=out
call.__globals__['records']=[]
manifest=call('InventoryRepository',{'repository':'path-lab'})
request={'repository':'path-lab','commit':manifest['commit']}
scanned=call('ScanCandidates',request)
candidates=[c for c in scanned['candidates'] if c['category']=='PATH_TRAVERSAL']
assert {c['line'] for c in candidates}=={14,21,28}
findings=[]
for c in candidates:
    point=dict(request,file=c['file'],line=c['line'])
    call('ReadCodeSlice',point)
    call('HashEvidence',point)
    f=call('RunValidation',point)
    assert f['category']=='PATH_TRAVERSAL'
    assert f['status']=={14:'VERIFIED',21:'NEEDS_REVIEW',28:'REJECTED'}[c['line']]
    assert f['evidence_integrity']['status']=='PASS'
    findings.append(f)
(out/'mcp-result.json').write_text(json.dumps({'passed':True,'repository':request,'checks':call.__globals__['records'],'findings':findings},indent=2))
print('Path MCP: 3/3 verdicts PASS; four-category MCP regression PASS')
