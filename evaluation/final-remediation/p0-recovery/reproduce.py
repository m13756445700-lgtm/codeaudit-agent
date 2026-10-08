"""Offline Phase 2 replay against fixed implementation. No LLM/network; never execute audited repository code.
Usage: python reproduce.py BASELINE_SOURCE HISTORICAL_ARCHIVE OUTPUT_DIRECTORY
"""
import sys,json,tarfile,hashlib,tempfile
from pathlib import Path
source,archive,out=map(lambda x:Path(x).resolve(),sys.argv[1:])
sys.path.insert(0,str(source))
from agent.v2.engine import Engine
from agent.v2.repository import snapshot,profile
from agent.v2.tools import ToolLayer
from agent.v2.transport import Local
import agent.v2.engine as implementation
EXPECTED='636771c80bf332f75a67c7c53c2fd956c018d4988709cd3349bf322d924a22bd'
assert hashlib.sha256(Path(implementation.__file__).read_bytes()).hexdigest()==EXPECTED
out.mkdir(parents=True,exist_ok=True)
ERROR='Feature absence requires fully read declared files; partial reads cannot establish absence'
class Scripted:
 model='scripted-reproduction-no-LLM'
 usage=[]
 def __init__(self,args):self.args=args;self.n=0
 def complete(self,*_):
  self.n+=1
  return {'role':'assistant','content':None,'tool_calls':[{'id':str(self.n),'type':'function','function':{'name':'settle_surface','arguments':json.dumps(self.args)}}]}
def build(src,workspace,args):
 a,m=snapshot(src,workspace)
 e=Engine(Scripted(args),Local(ToolLayer(a)),a,m,profile(a/'repo'),max_iterations=5)
 e.dispatch('submit_plan',{'plan':{'attack_surfaces':[args['surface']],'next_actions':['read'],'priorities':['bounded reproduction']}})
 return e
def read(e,path,start=1,end=None):
 args={'path':path,'start':start}
 if end is not None:args['end']=end
 return e.dispatch('use_tool',{'tool':'repo.read_range','arguments':args,'purpose':'offline reproduction evidence'})
def failed(e,args):
 try:e.dispatch('settle_surface',args)
 except ValueError as exc:
  e.reproduced_feedback = getattr(exc, 'feedback', None)
  return str(exc)
 raise AssertionError('Expected rejection')
def ranges(nums):
 result=[]
 for n in nums:
  if result and result[-1][1]+1==n:result[-1][1]=n
  else:result.append([n,n])
 return result
result={'real_model':False,'baseline_engine_sha256':EXPECTED,'historical_archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
assert result['historical_archive_sha256']=='e02f2a6c2ef55364c2e2aa0816e6f5260542162b37c50edae25e5473fd3f62cb'
with tempfile.TemporaryDirectory(prefix='p0-reproduction-') as tmp:
 tmp=Path(tmp);src=tmp/'minimal';src.mkdir();(src/'a.py').write_text('value = 1\n'*121)
 args={'surface':'minimal','status':'reviewed','files':['a.py'],'reason':'Synthetic fixture without storage feature; mechanical coverage test only','assessment':'feature_absent','decision_ids':[],'absence_evidence':[{'file':'a.py','line':1,'symbol':'value','evidence':'value = 1'}]}
 e=build(src,tmp/'minimal-ws',args);read(e,'a.py',1,120)
 err=failed(e,args);assert err==ERROR
 summary=e.run();assert summary['status']=='INCOMPLETE' and e.model.n==2
 trace=[json.loads(x) for x in (e.audit/'tool_calls.jsonl').read_text().splitlines()]
 (out/'minimal-trace.json').write_text(json.dumps(trace,indent=2))
 result['minimal']={'file_lines':121,'read_lines':120,'observer_missing_ranges':[[121,121]],'error':err,'initial_rejection_before_run':1,'structured_feedback':e.reproduced_feedback,'model_response_rounds':e.model.n,'run_summary':summary}
 read(e,'a.py',121,121);accepted=e.dispatch('settle_surface',args)
 result['manual_full_read_control']={'accepted':accepted,'note':'Script-directed missing-line read; not autonomous LLM recovery or semantic verification'}
 assert 'minimal' in e.surface_settlements
 with tarfile.open(archive) as tar:
  name=next(n for n in tar.getnames() if n.endswith('/tool_calls.jsonl'))
  prefix=name[:-len('tool_calls.jsonl')]
  events=[json.loads(x) for x in tar.extractfile(name)]
  index,event=next((i,x) for i,x in reversed(list(enumerate(events))) if x.get('tool')=='settle_surface' and x.get('result_summary',{}).get('error')==ERROR)
  args=json.loads(event['arguments']);hist=tmp/'historical';hist.mkdir()
  for path in args['files']:
   dest=hist/path;assert dest.resolve().is_relative_to(hist.resolve())
   dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(tar.extractfile(prefix+'repo/'+path).read())
  e=build(hist,tmp/'historical-ws',args)
  observed_events=[]
  for ev in events[:index]:
   r=ev.get('result_summary',{})
   if ev['tool'] in ('repo.read_file','repo.read_range') and r.get('file') in args['files'] and 'sha256' in r:
    assert r['sha256']==e.metadata['files'][r['file']]
    e.receipts.append({k:r[k] for k in ('file','sha256','start','end')})
    e.read_cache.setdefault(r['file'],{}).update({line['line']:line['code'] for line in r.get('lines',[])})
    observed_events.append({'tool':ev['tool'],'arguments':ev['arguments'],'timestamp':ev.get('timestamp')})
  gaps={}
  for path in args['files']:
   lines=(hist/path).read_text(errors='replace').splitlines();obs=e.read_cache[path]
   missing=[n for n,line in enumerate(lines,1) if obs.get(n)!=line]
   gaps[path]={'total_lines':len(lines),'observed_exact_lines':len(lines)-len(missing),'missing_ranges':ranges(missing)}
  err=failed(e,args);assert err==ERROR
  summary=e.run();assert summary['status']=='INCOMPLETE' and e.model.n==2
  result['historical_replay']={'audit_id':prefix.strip('./ /'),'event_index_zero_based':index,'original_event':event,'observer_coverage':gaps,'prior_reads':observed_events,'replayed_error':err,'initial_rejection_before_run':1,'structured_feedback':e.reproduced_feedback,'run_summary':summary,'scope':'Original final settlement arguments + original source bytes + accumulated successful read results. Retry control replayed, not entire original agent conversation.'}
  (out/'historical-replay-trace.json').write_text((e.audit/'tool_calls.jsonl').read_text())
  for path,details in gaps.items():
   for lo,hi in details['missing_ranges']:
    for start in range(lo,hi+1,120):read(e,path,start,min(start+119,hi))
  result['historical_manual_full_read_control']=e.dispatch('settle_surface',args)
  assert args['surface'] in e.surface_settlements
(out/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
print(json.dumps({'minimal_status':result['minimal']['run_summary']['status'],'historical_status':result['historical_replay']['run_summary']['status'],'historical_gaps':gaps,'manual_controls':'accepted','REAL_MODEL':False},indent=2))
