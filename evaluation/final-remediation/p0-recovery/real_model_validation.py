"""Induced recovery protocol trial: seeded partial read, all subsequent actions real LLM.
Credentials are inherited from the environment, never logged. Not a blind security benchmark.
"""
import sys,json,subprocess,hashlib
from pathlib import Path
from urllib.parse import urlparse
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from agent.v2.engine import Engine
from agent.v2.model import Model
from agent.v2.repository import snapshot,profile
from agent.v2.tools import ToolLayer
from agent.v2.transport import Local
out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=True)
assert not (out/'result.json').exists(), 'Preserve prior validation'
source=out/'source';source.mkdir()
(source/'inventory_constants.py').write_text('\n'.join('ITEM_%d = %d'%(n,n) for n in range(1,174))+'\n')
class RecordedModel(Model):
 def complete(self,messages,tools):
  number=len(self.usage)+1
  (out/('request-%02d.json'%number)).write_text(json.dumps({'messages':messages,'tools':tools},indent=2))
  response=super().complete(messages,tools)
  (out/('response-%02d.json'%number)).write_text(json.dumps(response,indent=2))
  return response
model=RecordedModel()
audit,meta=snapshot(source,out/'audits')
e=Engine(model,Local(ToolLayer(audit)),audit,meta,profile(audit/'repo'),max_iterations=12,max_calls=24,timeout=240)
plan={'attack_surfaces':['storage in declared constants module'],'next_actions':['attempt settlement and follow evidence feedback']}
e.dispatch('submit_plan',{'plan':plan})
read=e.dispatch('use_tool',{'tool':'repo.read_range','arguments':{'path':'inventory_constants.py','start':1,'end':120},'purpose':'Harness seeds partial read for induced rejection test'})
e.messages.append({'role':'user','content':json.dumps({'trial':'Induced recovery protocol validation, not vulnerability evaluation. The harness has already submitted this plan and performed the attached real read. Your immediate next action must be settle_surface with status reviewed, assessment feature_absent for storage in this declared file; cite ITEM_1 = 1 at line1, no decision_ids. Do not perform another read before this first attempt. Thereafter choose your own actions using authoritative tool feedback and finish honestly. No particular missing range or later action sequence is supplied.', 'plan':plan,'actual_read':read})})
summary=e.run()
events=[json.loads(line) for line in (audit/'tool_calls.jsonl').read_text().splitlines()]
rejections=[i for i,x in enumerate(events) if x.get('result_summary',{}).get('status')=='NEEDS_MORE_EVIDENCE']
sequence=[]
for x in events:
 sequence.append({k:x[k] for k in ('tool','arguments','purpose','result_summary','timestamp') if k in x})
passed=False
if rejections:
 i=rejections[0]
 reads=[j for j,x in enumerate(events) if j>i and x['tool'] in ('repo.read_range','repo.read_file') and x.get('result_summary',{}).get('file')=='inventory_constants.py' and x.get('result_summary',{}).get('end',0)>=173]
 settlements=[j for j,x in enumerate(events) if x['tool']=='settle_surface' and x.get('result_summary',{}).get('accepted') and isinstance(x.get('arguments'),dict) and x['arguments'].get('status')=='reviewed']
 passed=bool(reads and any(j>reads[0] for j in settlements) and summary['status']=='COMPLETE')
result={'REAL_MODEL':True,'REAL_MODEL_RECOVERY':'PASS' if passed else 'FAIL','provider':urlparse(model.endpoint).hostname,'model':model.model,'commit_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'audit_id':audit.name,'protocol':'Harness seeds plan/partial read and explicitly induces first settlement attempt. Every action after seeding, including rejected settlement, is selected by actual model. No next-action sequence injected after rejection. Local transport, not OctoBus E2E.','summary':summary,'action_sequence':sequence,'source_sha256':hashlib.sha256((source/'inventory_constants.py').read_bytes()).hexdigest()}
(out/'result.json').write_text(json.dumps(result,indent=2))
(out/'conversation.json').write_text(json.dumps(e.messages,indent=2))
print(json.dumps({k:result[k] for k in ('REAL_MODEL','REAL_MODEL_RECOVERY','provider','model','commit_sha','audit_id')}))
print(json.dumps({'workflow_status':summary['status'],'failure':summary['failure'],'tool_calls':summary['tool_calls'],'usage':summary['usage']}))
