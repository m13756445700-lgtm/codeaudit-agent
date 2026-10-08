import json,copy
from agent.v2.challenge import critique,SYSTEM
from test_v2_tools_gate import finding
class Capture:
    def complete(self,messages,tools):
        self.messages=messages
        return {'tool_calls':[{'function':{'name':'critique','arguments':json.dumps({'assessment':'Bounded advice only','objections':[]})}}]}

def test_critic_drops_evaluator_fields_and_preserves_finding():
    model=Capture();f=finding();f.update(expected='CANARY_EXPECTED',ground_truth='CANARY_TRUTH',answer='CANARY_ANSWER')
    f['environment_assumptions']=[{'claim':'OS unknown','state':'unknown','references':[],'affects_verdict':True,'expected':'NESTED_CANARY'}]
    before=copy.deepcopy(f)
    critique(model,f,{'app.py':{2:f['source']['evidence'],90:'UNREAD_OTHER_LOCATION'}},{})
    payload=json.loads(model.messages[1]['content']);encoded=json.dumps(payload)
    assert all(x not in encoded for x in ('CANARY_EXPECTED','CANARY_TRUTH','CANARY_ANSWER','NESTED_CANARY','UNREAD_OTHER_LOCATION'))
    assert f==before and payload['finding']['status']=='CONFIRMED'
    assert 'read_excerpts' in payload and len(model.messages)==2

def test_status_specific_challenges_are_advisory():
    for word in ['CONFIRMED','REJECTED','LIKELY','INSUFFICIENT_EVIDENCE','before the sink','another layer']:
        assert word in SYSTEM
    assert 'Do not return or rewrite a vulnerability verdict' in SYSTEM
