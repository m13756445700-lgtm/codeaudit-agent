"""Real-model recovery acceptance. Only observation/seeding, no product overrides.
Usage: python acceptance.py A|B|C OUTPUT
Model credentials come from process environment and are never serialized.
"""
import sys,json,hashlib,subprocess
from pathlib import Path
from urllib.parse import urlparse
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from agent.v2.model import Model
from agent.v2.engine import Engine
from agent.v2.recovery import NeedsMoreEvidence,coverage_gaps
from agent.v2.repository import snapshot,profile
from agent.v2.tools import ToolLayer
from agent.v2.transport import Local

def write(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def fixture(kind,source):
    source.mkdir(parents=True)
    if kind=='A':
        (source/'catalog.py').write_text('\n'.join('CATALOG_ENTRY_%d = %d'%(n,n) for n in range(1,181))+'\n')
        return ['catalog.py'], [('catalog.py',1,120),('catalog.py',121,150)], 'Determine whether this declared catalogue module implements SQL persistence. Review the declared file scope, investigate as needed, and finish with evidence-based scope and limitations.'
    (source/'controller.py').write_text('from service import fetch_invoice\n\ndef get_invoice(user, records, invoice_id):\n    return fetch_invoice(user, records, invoice_id)\n')
    (source/'service.py').write_text('from security_config import may_read\n\ndef fetch_invoice(user, records, invoice_id):\n    invoice = records[invoice_id]\n    if not may_read(user, invoice):\n        raise PermissionError("access denied")\n    return {"amount": invoice["amount"], "tenant_id": invoice["tenant_id"]}\n')
    lines=['POLICY_REVISION_%d = %d'%(n,n) for n in range(1,181)]
    # Evaluator-only setup; the source guard is ordinary code, not an injected instruction.
    at=150 if kind=='B' else 83
    lines[at:at+6]=['def may_read(user, invoice):','    if not user.get("authenticated", False):','        return False','    if user.get("tenant_id") != invoice.get("tenant_id"):', '        return False', '    return True']
    (source/'security_config.py').write_text('\n'.join(lines)+'\n')
    reads=[('controller.py',1,4),('service.py',1,7)]
    if kind=='B':reads += [('security_config.py',1,120),('security_config.py',121,150)]
    else:reads += [('security_config.py',1,83),('security_config.py',90,180)]
    return ['controller.py','service.py','security_config.py'],reads,'Assess whether invoice retrieval enforces authenticated same-tenant access across the declared controller, service and security configuration. Caller identity is an operator-supplied authenticated user context, and records is an operator-supplied invoice map; assess this conditional code scope, not unknown deployment. Investigate source and defenses and finish with evidence-based judgments and limitations.'

class Recorder(Model):
    def __init__(self,out):super().__init__();self.out=out;self.round=0;self.pending_calls=[]
    def complete(self,messages,tools):
        self.round+=1
        write(self.out/('request-%02d.json'%self.round),{'model':self.model,'messages':messages,'tools':tools,'tool_choice':'auto','max_tokens':3500,'temperature':0,'thinking':{'type':'disabled'}})
        r=super().complete(messages,tools)
        write(self.out/('response-%02d.json'%self.round),r)
        self.pending_calls=list(r.get('tool_calls') or [])
        return r

class ObservedEngine(Engine):
    def observe(self):
        return {'coverage':self.coverage(),'gaps':coverage_gaps(self,self.declared),
                'pending_evidence':json.loads(json.dumps(self.pending_evidence)),
                'surface_settlements':json.loads(json.dumps(self.surface_settlements))}
    def dispatch(self,name,args):
        before=self.observe();call_id=None
        if not self.seeding:
            call=self.model.pending_calls.pop(0)
            assert name==call['function']['name'] and args==json.loads(call['function']['arguments'])
            call_id=call['id']
        row={'sequence':len(self.transitions)+1,'origin':'HARNESS_SEED' if self.seeding else 'REAL_MODEL',
             'model_round':self.model.round,'tool_call_id':call_id,'action':name,'arguments':args,'before':before}
        try:
            result=super().dispatch(name,args)
            row['result']=result
            return result
        except NeedsMoreEvidence as e:
            row['gate_result']=json.loads(json.dumps(e.feedback));row['error']=str(e)
            raise
        except Exception as e:
            row['error']=type(e).__name__+': '+str(e)
            raise
        finally:
            row['after']=self.observe();self.transitions.append(row)
            with (self.output/'state-transitions.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')

def missing_count(row):
    return sum(end-start+1 for f in row['gaps'] for start,end in f['missing_ranges'])

def adjudicate(e,out,summary):
    rs=[r for r in e.transitions if r['origin']=='REAL_MODEL' and r.get('gate_result',{}).get('status')=='NEEDS_MORE_EVIDENCE' and r['action']=='settle_surface']
    if not rs:return {'status':'TEST_INCONCLUSIVE','reason':'NO_REJECTION_TRIGGERED','events':[]}
    proofs=[]
    for rejected in rs:
        surface=rejected['gate_result']['surface_id'];after=[r for r in e.transitions if r['sequence']>rejected['sequence'] and r['origin']=='REAL_MODEL']
        received=False
        for p in sorted(out.glob('request-*.json')):
            if int(p.stem.split('-')[-1])<=rejected['model_round']:continue
            for m in json.loads(p.read_text())['messages']:
                if m.get('role')=='tool' and m.get('tool_call_id')==rejected['tool_call_id']:
                    feedback=json.loads(m['content'])
                    received=feedback.get('status')=='NEEDS_MORE_EVIDENCE' and feedback.get('fingerprint')==rejected['gate_result']['fingerprint']
        reads=[r for r in after if r['action']=='use_tool' and r['arguments'].get('tool') in ('repo.read_file','repo.read_range') and missing_count(r['after'])<missing_count(r['before']) and 'result' in r]
        repeats=[r for r in after if r['action']=='settle_surface' and r['arguments']==rejected['arguments'] and 'gate_result' in r and r['gate_result']['fingerprint']==rejected['gate_result']['fingerprint']]
        accepted=[r for r in after if r['action']=='settle_surface' and r['arguments'].get('surface')==surface and r.get('result',{}).get('accepted')]
        proof={'first_settlement':rejected['sequence'],'gate_result':rejected['gate_result'],'rejection_received':received,'evidence_reads':[r['sequence'] for r in reads],'identical_failed_repeats':[r['sequence'] for r in repeats],'accepted_settlements':[r['sequence'] for r in accepted]}
        proofs.append(proof)
        if received and reads and not repeats and any(r['sequence']>reads[0]['sequence'] for r in accepted):
            return {'status':'PASS','reason':'SAME_AUDIT_REAL_MODEL_RECOVERY_OBSERVED','events':proofs}
    return {'status':'FAIL','reason':'REJECTION_OBSERVED_WITHOUT_COMPLETE_RECOVERY_PROOF','events':proofs}

def main():
    kind=sys.argv[1];out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=False)
    paths,reads,prompt=fixture(kind,out/'source');write(out/'prompt.json',{'task':prompt})
    model=Recorder(out);audit,meta=snapshot(out/'source',out/'audits')
    e=ObservedEngine(model,Local(ToolLayer(audit)),audit,meta,profile(audit/'repo'),max_iterations=20,max_calls=40,timeout=300)
    e.output=out;e.declared=paths;e.transitions=[];e.seeding=True
    plan={'attack_surfaces':['declared module review'],'next_actions':['Assess source evidence and relevant defenses'],'priorities':['bounded declared file scope']}
    e.dispatch('submit_plan',{'plan':plan});payload=[]
    for path,start,end in reads:payload.append(e.dispatch('use_tool',{'tool':'repo.read_range','arguments':{'path':path,'start':start,'end':end},'purpose':'Read initial investigation source'}))
    e.messages.append({'role':'user','content':json.dumps({'task':prompt,'declared_files':paths,'initial_investigation':{'notice':'Harness-seeded plan and actual tool reads, not prior model actions or validated conclusions. Continue this audit using the available capabilities.','accepted_plan':plan,'read_results':payload}},ensure_ascii=False)})
    e.seeding=False;write(out/'initial-state.json',e.observe())
    summary=e.run();outcome=adjudicate(e,out,summary)
    result={'REAL_MODEL':True,'fixture':kind,'provider':urlparse(model.endpoint).hostname,'model':model.model,'commit_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'audit_id':audit.name,'conversation_run_id':audit.name,'outcome':outcome,'summary':summary,'final_state':e.observe(),'transport':'Local read-only tools; not OctoBus E2E','product_code_changed':False}
    write(out/'result.json',result);write(out/'final-context.json',e.messages)
    write(out/'SHA256SUMS.json',{str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file()})
    print(json.dumps({'audit_id':audit.name,'outcome':outcome,'workflow':summary['status'],'failure':summary['failure'],'calls':summary['tool_calls'],'tokens':sum(x.get('total_tokens',0) for x in model.usage)}))
if __name__=='__main__':main()
