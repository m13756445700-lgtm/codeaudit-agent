"""Bounded three-arm heldout-style evaluation. Labels never passed to Engine."""
import json,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent.v2.engine import Engine
from agent.v2.model import Model
from agent.v2.repository import snapshot,profile
from agent.v2.tools import ToolLayer
from agent.v2.transport import Local
GENERIC='Inspect untrusted input and its reachable sinks. Verify defenses and preconditions. Do not assume deployment. Cite exact read evidence. Abstain on unresolved decisive semantics.'
class Generic:
    kind='local+explicit-generic-ablation'
    def __init__(self,inner):self.inner=inner
    def call(self,name,args):
        if name=='knowledge.retrieve':return {'id':'generic-security','sha256':hashlib.sha256(GENERIC.encode()).hexdigest(),'content':GENERIC}
        return self.inner.call(name,args)

def model_input(case):
    # The only evaluator-manifest field sent to the investigator is the normal task.
    return case['task']

def score(case,summary,findings):
    positives=[f for f in findings if f.get('status') in ('CONFIRMED','LIKELY')]
    relevant=[f for f in findings if f.get('category')==case['category']]
    claimed=any(f.get('status') in ('CONFIRMED','LIKELY') for f in relevant)
    negative=any(f.get('status')=='REJECTED' for f in relevant)
    absence=any(r.get('assessment')=='feature_absent' for r in (summary.get('completion') or {}).get('surface_reviews',[]))
    abstain=not claimed and not negative and not absence
    expected=case['expected_positive'];confusion=('TP' if claimed else 'FN') if expected else ('FP' if claimed else ('TN' if not abstain else 'ABSTAIN'))
    if abstain:confusion='ABSTAIN'
    ref=case['decisive_reference']
    matches=[f for f in relevant if any(isinstance(r,dict) and r.get('file')==ref['file'] and r.get('line')==ref['line'] for r in [f.get('source'),f.get('sink'),*f.get('data_flow',[]),*f.get('counter_evidence',[])])]
    return {'confusion':confusion,'abstention':abstain,'correctness':confusion in ('TP','TN'),'completion':summary['status']=='COMPLETE','extra_positive_findings':len([f for f in positives if f not in relevant]),'decisive_reference_cited':bool(matches),'all_reference_gates_pass':all(f.get('evidence_gate',{}).get('passed',False) for f in findings),'evidence_quality_limit':'Reference checks and target match only; manual semantic adjudication required. No claim of proven flow or true positive from quote integrity alone.'}

class Recorded(Model):
    def __init__(self,out):super().__init__();self.out=out;self.n=0
    def complete(self,messages,tools):
        self.n+=1
        (self.out/('request-%02d.json'%self.n)).write_text(json.dumps({'messages':messages,'tools':tools}))
        response=super().complete(messages,tools)
        (self.out/('response-%02d.json'%self.n)).write_text(json.dumps(response))
        return response

def run(cid,arm,out):
    manifest=json.loads(Path('evaluation/p1-heldout/manifest.json').read_text());case=next(c for c in manifest['cases'] if c['id']==cid)
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    source=Path('evaluation/p1-heldout')/cid/'source'
    assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()}==case['files']
    audit,meta=snapshot(source,out/'audits');transport=Local(ToolLayer(audit))
    if arm=='generic':transport=Generic(transport)
    model=Recorded(out);summary=Engine(model,transport,audit,meta,profile(audit/'repo'),max_iterations=18,max_calls=36,timeout=300,knowledge=arm!='off',focus=model_input(case),adversarial_review=True).run()
    findings=json.loads((audit/'findings.json').read_text())
    result={'case':cid,'arm':arm,'REAL_MODEL':True,'model':model.model,'audit_id':audit.name,'summary':summary,'findings':findings,'metrics':score(case,summary,findings),'tool_calls':summary['tool_calls'],'tokens':sum(x.get('total_tokens',0) for x in model.usage)}
    (out/'result.json').write_text(json.dumps(result,indent=2));return result
if __name__=='__main__':print(json.dumps(run(sys.argv[1],sys.argv[2],sys.argv[3])))
