"""Real MCP smoke test against the isolated local OctoBus container."""
import json, os, secrets, subprocess, urllib.request, urllib.error
from pathlib import Path
D = os.environ.get('CODEAUDIT_DOCKER', '/Applications/Docker.app/Contents/Resources/bin/docker')
CONTAINER = os.environ.get('CODEAUDIT_OCTOBUS_CONTAINER', 'codeaudit-local-octobus')
OUT = Path(__file__).resolve().parents[1] / 'runs/local-recheck'
BASE = os.environ.get('CODEAUDIT_MCP_URL', 'http://127.0.0.1:19000/capsets/code-audit-agent/mcp')
OUT.mkdir(parents=True, exist_ok=True)
TOKEN_FILE = OUT / 'local-capset.token'
if TOKEN_FILE.exists():
    token = TOKEN_FILE.read_text().strip()
else:
    token = secrets.token_urlsafe(32)
    TOKEN_FILE.write_text(token)
    TOKEN_FILE.chmod(0o600)
    p = subprocess.run([D,'exec','-i',CONTAINER,'octobus','capset','add-token','code-audit-agent','local-verification','--token-stdin'],input=token,text=True,capture_output=True)
    if p.returncode:
        raise RuntimeError('Token registration failed')
session = None
counter = 0
records = []
def rpc(method, params, credential=token, notification=False):
    global session, counter
    counter += 1
    data = {'jsonrpc':'2.0','method':method,'params':params}
    if not notification: data['id']=counter
    headers = {'Content-Type':'application/json','Accept':'application/json, text/event-stream','MCP-Protocol-Version':'2025-03-26'}
    if credential is not None: headers['Authorization']='Bearer '+credential
    if session: headers['Mcp-Session-Id']=session
    req = urllib.request.Request(BASE,json.dumps(data).encode(),headers)
    try:
        with urllib.request.urlopen(req,timeout=160) as response:
            session = response.headers.get('Mcp-Session-Id',session)
            raw = response.read().decode()
            status=response.status
    except urllib.error.HTTPError as exc:
        return exc.code, None
    if not raw.strip(): return status,None
    if raw.lstrip().startswith('data:') or '\ndata:' in raw:
        values=[json.loads(line[5:].strip()) for line in raw.splitlines() if line.startswith('data:')]
        parsed=next((x for x in values if x.get('id')==counter),values[-1])
    else: parsed=json.loads(raw)
    return status,parsed
for label, credential in [('missing',None),('invalid','invalid-local-test')]:
    status,_ = rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'codeaudit-verifier','version':'1'}},credential)
    assert status==401,(label,status)
    records.append({'test':'auth-'+label,'status':status,'pass':True})
status,init=rpc('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'codeaudit-verifier','version':'1'}})
assert status==200 and 'result' in init,init
rpc('notifications/initialized',{},notification=True)
_,listing=rpc('tools/list',{})
tools=listing['result']['tools']
(OUT/'tools-list.json').write_text(json.dumps(listing,indent=2))
assert len(tools)==5,tools
print('MCP tools:',[t['name'] for t in tools],flush=True)
def call(method, request, expect_error=False):
    tool=next(t for t in tools if t['name'].replace('_','').lower().endswith(method.lower()))
    schema=tool['inputSchema']['properties']
    field='requestJson' if 'requestJson' in schema else 'request_json'
    status,result=rpc('tools/call',{'name':tool['name'],'arguments':{field:json.dumps(request)}})
    (OUT/(str(counter)+'-'+method+('-negative' if expect_error else '')+'.json')).write_text(json.dumps(result,indent=2))
    failed = 'error' in result or result.get('result',{}).get('isError',False) or 'error' in result.get('result',{}).get('structuredContent',{})
    if expect_error:
        assert failed,result
        records.append({'test':method+'-negative','pass':True})
        return
    assert status==200 and not failed,result
    content=result['result']
    payload=content.get('structuredContent')
    if payload is None: payload=json.loads(next(c['text'] for c in content['content'] if c['type']=='text'))
    if 'resultJson' in payload: payload=json.loads(payload['resultJson'])
    if 'result_json' in payload: payload=json.loads(payload['result_json'])
    records.append({'test':method,'run_id':payload['run_id'],'pass':True})
    print(method,'PASS',flush=True)
    return payload['result']
manifest=call('InventoryRepository',{'repository':'lab'})
request={'repository':'lab','commit':manifest['commit']}
scan=call('ScanCandidates',request)
assert len(scan['candidates'])==2,scan
point={**request,'file':'src/main/resources/mapper/UserMapper.xml','line':5}
call('ReadCodeSlice',point)
call('HashEvidence',point)
finding=call('RunValidation',point)
assert finding['status']=='VERIFIED',finding
assert all(k in finding for k in ['source','dataflow','sink','protection','reachability','evidence_integrity']),finding
safe=call('RunValidation',{**point,'line':8})
assert safe['status']=='REJECTED',safe
call('InventoryRepository',{'repository':'../'},True)
call('ReadCodeSlice',{'repository':'lab','file':'/etc/passwd','line':1},True)
call('ReadCodeSlice',{**request,'file':'../../etc/passwd','line':1},True)
call('ReadCodeSlice',{**point,'end_line':105},True)
(OUT/'phase6-result.json').write_text(json.dumps({'passed':True,'commit':manifest['commit'],'checks':records},indent=2))
print('Phase 6 MCP verification PASS')
