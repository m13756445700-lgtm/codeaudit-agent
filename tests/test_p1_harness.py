import json
from scripts.p1_knowledge_eval import model_input,score,Generic

def test_evaluator_labels_excluded_from_input():
    case={'task':'Review source','expected_positive':'CANARY','decisive_reference':'CANARY','category':'CANARY'}
    assert model_input(case)=='Review source'

def test_abstention_is_not_tn_or_success():
    c={'category':'authz','expected_positive':False,'decisive_reference':{'file':'a','line':1}}
    m=score(c,{'status':'INCOMPLETE'},[])
    assert m['confusion']=='ABSTAIN' and not m['correctness'] and not m['completion']

def test_generic_knowledge_never_reads_project_documents():
    class Inner:
        def call(self,*_):raise AssertionError('Project knowledge must not be fetched')
    result=Generic(Inner()).call('knowledge.retrieve',{'category':'authz'})
    assert result['id']=='generic-security'

def test_manifest_source_integrity_and_no_evaluator_labels_in_snapshot():
    from pathlib import Path
    import hashlib
    root=Path('evaluation/p1-heldout');m=json.loads((root/'manifest.json').read_text())
    assert len(m['cases'])==6 and m['max_runs']==18
    for c in m['cases']:
        files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/c['id']/'source').iterdir()}
        assert files==c['files'] and 'manifest.json' not in files
