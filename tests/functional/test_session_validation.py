import copy
import json
import pytest
from agent.workflow.validation import verify_session, OutputError

@pytest.fixture
def trusted_session(tmp_path):
    commit='b'*40
    findings=[{'status':'VERIFIED'},{'status':'REJECTED'}]
    ids=['a'*32,'c'*32]
    events=[]
    def call(method,request,result,run_id='d'*32):
        events.append({'type':'event_msg','payload':{'type':'mcp_tool_call_end','invocation':{'server':'octobus','tool':'code-audit-service__code-audit-local__'+method,'arguments':{'request_json':json.dumps(request)}},'result':{'Ok':{'structuredContent':{'resultJson':json.dumps({'run_id':run_id,'result':result})}}}}})
    request={'repository':'lab','commit':commit}
    call('inventory_repository',request,{'commit':commit})
    call('scan_candidates',request,{'commit':commit,'candidates':[{'file':'Mapper.xml','line':5},{'file':'Mapper.xml','line':8}]})
    for line,run_id,finding in zip([5,8],ids,findings):
        point={**request,'file':'Mapper.xml','line':line}
        call('read_code_slice',point,{'snippet':'sql'})
        call('hash_evidence',point,{'reference':{}})
        call('run_validation',point,finding,run_id)
        folder=tmp_path/run_id;folder.mkdir()
        (folder/'validation-result.json').write_text(json.dumps({**request,'finding':finding}))
    final={**request,'validation_run_ids':ids,'findings':findings}
    events.append({'type':'event_msg','payload':{'type':'task_complete','last_agent_message':json.dumps(final)}})
    return events,tmp_path,final

def test_complete_session(trusted_session):
    events,root,value=trusted_session
    assert verify_session(events,root,'lab','b'*40)==value

@pytest.mark.parametrize('mutation',['omit','status','scope','markdown','replay','missing_read','tool_error','shell'])
def test_untrusted_or_incomplete_session_rejected(trusted_session,mutation):
    events,root,value=trusted_session
    if mutation=='omit':
        value['findings']=value['findings'][:1];value['validation_run_ids']=value['validation_run_ids'][:1]
    elif mutation=='status': value['findings'][1]['status']='VERIFIED'
    elif mutation=='scope': value['repository']='different'
    elif mutation=='replay':
        folder=root/('e'*32);folder.mkdir()
        (folder/'validation-result.json').write_text((root/('a'*32)/'validation-result.json').read_text())
        value['validation_run_ids'][0]='e'*32
    elif mutation=='missing_read': events.pop(2)
    elif mutation=='tool_error': events[2]['payload']['result']={'Ok':{'structuredContent':{'error':{'message':'failed'}}}}
    elif mutation=='shell': events.insert(0,{'type':'event_msg','payload':{'type':'exec_command_begin'}})
    events[-1]['payload']['last_agent_message']=json.dumps(value)
    if mutation=='markdown': events[-1]['payload']['last_agent_message']='```json\n'+json.dumps(value)+'\n```'
    with pytest.raises(OutputError): verify_session(events,root,'lab','b'*40)
