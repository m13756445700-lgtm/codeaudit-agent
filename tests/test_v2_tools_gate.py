import json
import pytest
from agent.v2.repository import snapshot, profile
from agent.v2.tools import ToolLayer
from agent.v2.gate import validate
from agent.v2.engine import Engine
from agent.v2.transport import Local


@pytest.fixture
def context(tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    (src / 'app.py').write_text('def view(request):\n    value = request.args["q"]\n    return wrapper(value)\n')
    (src / 'db.py').write_text('def wrapper(value):\n    return db.execute(value)\n')
    audit, meta = snapshot(src, tmp_path / 'ws')
    return audit, meta, ToolLayer(audit)


def finding():
    source = {'file': 'app.py', 'line': 2, 'symbol': 'view', 'evidence': 'value = request.args["q"]'}
    sink = {'file': 'db.py', 'line': 2, 'symbol': 'wrapper', 'evidence': 'return db.execute(value)'}
    return {'id': 'H1', 'title': 'SQL injection', 'category': 'sql_injection', 'status': 'CONFIRMED',
            'source': source, 'sink': sink, 'data_flow': [source, sink], 'reasoning_summary': 'Caller forwards input.',
            'false_positive_analysis': 'No binding in inspected code.', 'sanitizer_analysis': 'No sanitizer.',
            'exploit_preconditions': ['Endpoint exposed'], 'reachability': 'view calls wrapper',
            'controllability': 'request argument', 'security_boundary': 'HTTP to database',
            'confidence_rationale': 'Read caller and sink', 'unknowns': [], 'counter_evidence': [],
            'remediation': 'Bind parameters', 'confidence': 'high', 'severity': 'high', 'knowledge_used': [],
            'defense_claims': [], 'environment_assumptions': [],
            'judgment_scope':'deployment', 'deployment_exposure':'unknown'}


def test_gate_does_not_decide_vulnerability(context):
    audit, meta, tools = context
    receipts = [tools.read('app.py'), tools.read('db.py')]
    f = finding()
    assert validate(f, audit/'repo', meta, receipts, {})['status'] == 'CONFIRMED'
    f['status'] = 'REJECTED'
    f['counter_evidence'] = [f['sink']]
    assert validate(f, audit/'repo', meta, receipts, {})['status'] == 'REJECTED'


@pytest.mark.parametrize('mutation', ['line', 'quote', 'symbol', 'not_read', 'tamper'])
def test_gate_rejects_hallucination_and_unread(context, mutation):
    audit, meta, tools = context
    receipts = [tools.read('app.py'), tools.read('db.py')]
    f = finding()
    if mutation == 'line': f['sink']['line'] = 99
    if mutation == 'quote': f['sink']['evidence'] = 'invented'
    if mutation == 'symbol': f['sink']['symbol'] = 'absent'
    if mutation == 'not_read': receipts = receipts[:1]
    if mutation == 'tamper':
        p = audit/'repo/db.py'
        p.chmod(0o600)
        p.write_text('changed')
    checked = validate(f, audit/'repo', meta, receipts, {})
    assert checked['status'] == 'INSUFFICIENT_EVIDENCE'
    assert not checked['evidence_gate']['passed']


def test_capability_limits_and_search(context):
    audit, meta, tools = context
    result = tools.call('repo.find_references', {'query': 'wrapper'})
    assert len(result['matches']) == 2
    with pytest.raises(ValueError): tools.call('repo.read_file', {'path': '../metadata.json'})
    with pytest.raises(ValueError): tools.call('shell', {'query': 'id'})
    with pytest.raises(ValueError): tools.call('repo.read_range', {'path': 'app.py', 'end': 900})
    assert tools.call('knowledge.retrieve', {'category': 'sql_injection'})['sha256']


def test_missing_model_never_falls_back(monkeypatch):
    from agent.v2.model import Model
    monkeypatch.delenv('LLM_API_KEY', raising=False)
    with pytest.raises(ValueError): Model()


def test_incomplete_model_run_is_not_success(context):
    class BrokenModel:
        model = 'unit-test-double'
        usage = []
        def complete(self, messages, tools):
            raise RuntimeError('Unavailable')
    audit, meta, tools = context
    summary = Engine(BrokenModel(), Local(tools), audit, meta, profile(audit/'repo')).run()
    assert summary['status'] == 'INCOMPLETE'
    assert json.loads((audit/'findings.json').read_text()) == []


def test_defense_claim_must_quote_read_implementation(context):
    audit, meta, tools = context
    receipts = [tools.read('app.py'), tools.read('db.py')]
    f = finding()
    f['defense_claims'] = [{'claim': 'Rejects leading slash', 'references': [
        dict(f['sink'], evidence='filename.startswith("/")')], 'limitations': ''}]
    checked = validate(f, audit/'repo', meta, receipts, {})
    assert not checked['evidence_gate']['passed']
    assert any('quote not at cited line' in p for p in checked['evidence_gate']['problems'])


def test_import_cannot_prove_defense(tmp_path):
    src = tmp_path/'src'
    src.mkdir()
    (src/'app.py').write_text('from security import safe_join\n')
    audit, meta = snapshot(src, tmp_path/'ws')
    tools = ToolLayer(audit)
    ref = {'file': 'app.py', 'line': 1, 'symbol': 'safe_join',
           'evidence': 'from security import safe_join'}
    f = finding()
    f.update(status='REJECTED', source=ref, sink=ref, data_flow=[ref], counter_evidence=[ref],
             defense_claims=[{'claim': 'Traversal prevented', 'references': [ref], 'limitations': ''}])
    checked = validate(f, audit/'repo', meta, [tools.read('app.py')], {})
    assert checked['status'] == 'INSUFFICIENT_EVIDENCE'
    assert any('import is not implementation' in p for p in checked['evidence_gate']['problems'])


@pytest.mark.parametrize('status', ['CONFIRMED', 'LIKELY', 'REJECTED', 'INSUFFICIENT_EVIDENCE'])
def test_unknown_material_platform_cannot_settle_verdict(context, status):
    audit, meta, tools = context
    f = finding()
    f.update(status=status, counter_evidence=[f['sink']], environment_assumptions=[{
        'claim': 'Deployment OS is Linux', 'state': 'unknown', 'references': [], 'affects_verdict': True}])
    checked = validate(f, audit/'repo', meta, [tools.read('app.py'), tools.read('db.py')], {})
    assert checked['status'] == 'INSUFFICIENT_EVIDENCE'
    assert checked['evidence_gate']['passed'] == (status == 'INSUFFICIENT_EVIDENCE')


def test_verified_platform_needs_read_evidence(context):
    audit, meta, tools = context
    f = finding()
    f['environment_assumptions'] = [{'claim': 'Linux deployment', 'state': 'verified',
                                     'references': [], 'affects_verdict': True}]
    checked = validate(f, audit/'repo', meta, [tools.read('app.py'), tools.read('db.py')], {})
    assert not checked['evidence_gate']['passed']


def test_real_but_irrelevant_reference_remains_a_documented_gate_limit(context):
    audit, meta, tools = context
    f = finding()
    f['defense_claims'] = [{'claim': 'Tenant authorization is enforced',
                           'references': [f['sink']], 'limitations': ''}]
    # db.execute(value) is real but cannot substantiate this claim. The Gate
    # deliberately cannot replace semantic review with a lexical detector.
    checked = validate(f, audit/'repo', meta, [tools.read('app.py'), tools.read('db.py')], {})
    assert checked['evidence_gate']['passed']


def test_finish_requires_review_of_exact_decision_revision(context):
    audit, meta, tools = context
    engine = Engine(None, Local(tools), audit, meta, profile(audit/'repo'), knowledge=False)
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces':['database'], 'next_actions':['read']}})
    for path in ('app.py', 'db.py'):
        engine.dispatch('use_tool', {'tool':'repo.read_file','arguments':{'path':path},'purpose':'inspect'})
    engine.dispatch('hypothesis', {'hypothesis':{'id':'H1','statement':'Input reaches query','status':'INVESTIGATING'}})
    f = finding(); f['knowledge_application'] = 'Disabled for test'
    engine.dispatch('submit_decision', {'finding':f})
    finish = {'summary':'Bounded audit', 'limitations':['Deployment unknown'], 'surface_reviews':[
        {'surface':'database','status':'reviewed','files':['app.py','db.py'],'reason':'Read caller and query','assessment':'decision','decision_ids':['H1'],'absence_evidence':[]}]}
    with pytest.raises(ValueError, match='self-review'):
        engine.dispatch('finish', finish)
    review = {'id':'H1','counterexample':'Does wrapper bind parameters?',
              'assessment':'Read call passes the value as query text.', 'outcome':'upheld','references':[f['sink']]}
    bad = dict(review, references=[dict(f['sink'], evidence='not real')])
    with pytest.raises(ValueError, match='evidence invalid'):
        engine.dispatch('review_decision', bad)
    assert engine.pending_decision_reviews() == ['H1']
    engine.dispatch('review_decision', dict(review, outcome='revise'))
    with pytest.raises(ValueError, match='self-review'):
        engine.dispatch('finish', finish)
    engine.dispatch('review_decision', review)
    assert engine.pending_decision_reviews() == []
    f['reasoning_summary'] = 'Revised analysis of the caller and query'
    engine.dispatch('submit_decision', {'finding':f})
    assert engine.pending_decision_reviews() == ['H1']
    engine.dispatch('review_decision', review)
    engine.dispatch('finish', finish)
    assert engine.status == 'COMPLETE'
    saved = json.loads((audit/'decision_reviews.json').read_text())
    assert saved[0]['kind'] == 'model_self_review'


def test_conditional_code_flaw_is_not_erased_by_unknown_deployment(context):
    audit, meta, tools = context
    f = finding()
    claim = 'Application exposes this query to untrusted input'
    f.update(judgment_scope='conditional_code', deployment_exposure='unknown',
             exploit_preconditions=[claim], environment_assumptions=[{
                 'claim':claim,'state':'unknown','affects_verdict':True,'references':[]}])
    receipts = [tools.read('app.py'),tools.read('db.py')]
    checked = validate(f,audit/'repo',meta,receipts,{})
    assert checked['status'] == 'CONFIRMED' and checked['deployment_exposure'] == 'unknown'
    f['judgment_scope'] = 'deployment'
    assert validate(f,audit/'repo',meta,receipts,{})['status'] == 'INSUFFICIENT_EVIDENCE'
    f['judgment_scope'] = 'conditional_code'; f['exploit_preconditions'] = []
    assert validate(f,audit/'repo',meta,receipts,{})['status'] == 'INSUFFICIENT_EVIDENCE'
    f['exploit_preconditions'] = [claim];f['deployment_exposure'] = 'evidenced'
    assert validate(f,audit/'repo',meta,receipts,{})['status'] == 'INSUFFICIENT_EVIDENCE'


def test_definition_header_cannot_prove_defense(context):
    audit, meta, tools = context
    f = finding()
    f.update(status='REJECTED',counter_evidence=[{'file':'db.py','line':1,
             'symbol':'wrapper','evidence':'def wrapper(value):'}])
    checked = validate(f,audit/'repo',meta,[tools.read('app.py'),tools.read('db.py')],{})
    assert checked['status'] == 'INSUFFICIENT_EVIDENCE'
    assert any('definition header' in x for x in checked['evidence_gate']['problems'])


def test_failed_precondition_feedback_replays_actual_model_proposal(tmp_path):
    from pathlib import Path
    replay = json.loads((Path(__file__).parent/'fixtures/acceptance-replay12/proposal.json').read_text())
    src = tmp_path/'src'; src.mkdir()
    for name, content in replay['sources'].items():
        path = src/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content)
    audit, meta = snapshot(src, tmp_path/'ws')
    tools = ToolLayer(audit)
    receipts = []
    for name, content in replay['sources'].items():
        lines = content.splitlines()
        for start in range(1, len(lines)+1, 120):
            receipts.append(tools.read(name, start, min(start+119, len(lines))))
    f = replay['proposal']
    knowledge = {name:'test-replay-known-card' for name in f['knowledge_used']}
    rejected = validate(f, audit/'repo', meta, receipts, knowledge)
    assert not rejected['evidence_gate']['passed']
    claim = f['environment_assumptions'][0]['claim']
    assert json.dumps(claim, ensure_ascii=False) in rejected['evidence_gate']['problems'][0]
    # Simulate a model-authored correction; the Gate must not insert this itself.
    assert claim not in f['exploit_preconditions']
    f['exploit_preconditions'].append(claim)
    accepted = validate(f, audit/'repo', meta, receipts, knowledge)
    assert accepted['evidence_gate']['passed'], accepted['evidence_gate']['problems']
    assert accepted['status'] == f['status']
