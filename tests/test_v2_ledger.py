import json
import pytest
from agent.v2.engine import Engine
from agent.v2.repository import snapshot, profile
from agent.v2.tools import ToolLayer
from agent.v2.transport import Local


def make_engine(tmp_path):
    source = tmp_path/'input'; source.mkdir()
    (source/'a.py').write_text('value = input()\nprint(value)\n')
    directory, metadata = snapshot(source, tmp_path/'ws')
    engine = Engine(None, Local(ToolLayer(directory)), directory, metadata, profile(directory/'repo'))
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces': ['input', 'storage'], 'next_actions': ['read']}})
    engine.dispatch('use_tool', {'tool': 'repo.read_file', 'arguments': {'path': 'a.py'}, 'purpose': 'inspect'})
    return engine


def test_notes_require_actual_read_quote_and_survive_compaction(tmp_path):
    engine = make_engine(tmp_path)
    note = {'id': 'N1', 'summary': 'Input reaches output; no database examined.',
            'references': [{'file': 'a.py', 'line': 1, 'symbol': 'value', 'evidence': 'value = input()'}],
            'open_questions': ['Is there a storage path?'], 'next_action': 'Inspect remaining files'}
    engine.dispatch('investigation_note', note)
    assert not engine.findings
    bad = dict(note, references=[dict(note['references'][0], line=99)])
    with pytest.raises(ValueError, match='actually read'):
        engine.dispatch('investigation_note', bad)
    assert engine.notes['N1'] == note
    engine.messages.append({'role':'user', 'content':'x'*90000})
    engine.compact_context()
    assert json.loads(engine.messages[2]['content'])['investigation_notes'] == [note]


def test_incremental_settlement_cannot_skip_unreviewed_surface(tmp_path):
    engine = make_engine(tmp_path)
    engine.dispatch('settle_surface', {'surface':'input', 'status':'reviewed', 'files':['a.py'], 'reason':'No database use in this input/output fixture', 'assessment':'feature_absent', 'decision_ids':[], 'absence_evidence':[{'file':'a.py','line':2,'symbol':'print','evidence':'print(value)'}]})
    assert not engine.finished
    with pytest.raises(ValueError, match='Unsettled'):
        engine.dispatch('finish', {'summary':'Review done', 'limitations':[], 'surface_reviews':[]})
    engine.dispatch('settle_surface', {'surface':'storage', 'status':'deferred', 'files':[], 'reason':'Not examined'})
    with pytest.raises(ValueError, match='limitations'):
        engine.dispatch('finish', {'summary':'Review done', 'limitations':[], 'surface_reviews':[]})
    engine.dispatch('finish', {'summary':'Bounded review', 'limitations':['Storage unexamined'], 'surface_reviews':[]})
    assert engine.status == 'PARTIAL'


def test_surface_rejects_unread_files(tmp_path):
    engine = make_engine(tmp_path)
    with pytest.raises(ValueError, match='actually read'):
        engine.dispatch('settle_surface', {'surface':'input', 'status':'reviewed', 'files':['missing.py'], 'reason':'claim'})
    assert not engine.surface_settlements


def test_segment_requires_new_evidence_checkpoint_without_promoting_status(tmp_path):
    engine = make_engine(tmp_path)
    request = {'tool':'repo.read_file', 'arguments':{'path':'a.py'}, 'purpose':'inspect'}
    for _ in range(11):
        engine.dispatch('use_tool', request)
    with pytest.raises(ValueError, match='segment exhausted'):
        engine.dispatch('use_tool', request)
    assert engine.status == 'RUNNING' and not engine.findings
    note = {'id':'N1', 'summary':'Input read; storage still unexamined',
            'references':[{'file':'a.py','line':1,'symbol':'value','evidence':'value = input()'}],
            'open_questions':['Storage use?'], 'next_action':'Search storage callers'}
    engine.dispatch('investigation_note', note)
    assert engine.segment_calls == 0
    engine.dispatch('use_tool', request)
    result = engine.dispatch('investigation_note', note)
    assert result['unchanged'] and engine.segment_calls == 1
    state = engine.investigation_checkpoint(1)
    assert state['segment']['remaining_capability_calls'] == 11
    assert not engine.surface_settlements


def test_unchanged_settlement_does_not_extend_investigation(tmp_path):
    engine = make_engine(tmp_path)
    review = {'surface':'input','status':'reviewed','files':['a.py'],'reason':'No database sink in fixture', 'assessment':'feature_absent', 'decision_ids':[], 'absence_evidence':[{'file':'a.py','line':2,'symbol':'print','evidence':'print(value)'}]}
    engine.dispatch('settle_surface', review)
    result = engine.dispatch('settle_surface', review)
    assert result['unchanged'] and result['remaining'] == ['storage']
    assert engine.segment_calls == 1 and not engine.finished


def test_surface_only_safety_claim_cannot_finish_or_settle(tmp_path):
    engine = make_engine(tmp_path)
    old = {'surface':'input','status':'reviewed','files':['a.py'],'reason':'No vulnerability; all defenses effective'}
    with pytest.raises(ValueError, match='explicit decision'):
        engine.dispatch('settle_surface',old)
    reviews = [old,dict(old,surface='storage')]
    with pytest.raises(ValueError, match='explicit decision'):
        engine.dispatch('finish',{'summary':'All safe','limitations':[],'surface_reviews':reviews})
    with pytest.raises(ValueError, match='existing decision'):
        engine.dispatch('settle_surface',dict(old,assessment='decision',decision_ids=['invented']))
    assert not engine.finished and not engine.surface_settlements


def test_absence_cannot_be_claimed_with_unread_quote(tmp_path):
    engine = make_engine(tmp_path)
    review = {'surface':'storage','status':'reviewed','files':['a.py'],'reason':'No database in tiny fixture',
              'assessment':'feature_absent','decision_ids':[],
              'absence_evidence':[{'file':'a.py','line':2,'symbol':'print','evidence':'no database access'}]}
    with pytest.raises(ValueError,match='Absence evidence'):
        engine.dispatch('settle_surface',review)


def test_sampled_lines_cannot_establish_feature_absence(tmp_path):
    engine = make_engine(tmp_path)
    engine.read_cache['a.py'].pop(2)
    review = {'surface':'storage','status':'reviewed','files':['a.py'],'reason':'No database',
              'assessment':'feature_absent','decision_ids':[],
              'absence_evidence':[{'file':'a.py','line':1,'symbol':'value','evidence':'value = input()'}]}
    with pytest.raises(ValueError,match='fully read'):
        engine.dispatch('settle_surface',review)


def test_absence_rechecks_snapshot_integrity(tmp_path):
    engine = make_engine(tmp_path)
    path = engine.audit/'repo/a.py';path.chmod(0o600);path.write_text('eval(input())\n')
    review = {'surface':'storage','status':'reviewed','files':['a.py'],'reason':'No database',
              'assessment':'feature_absent','decision_ids':[],
              'absence_evidence':[{'file':'a.py','line':1,'symbol':'value','evidence':'value = input()'}]}
    with pytest.raises(ValueError,match='snapshot changed'):
        engine.dispatch('settle_surface',review)


def test_cross_file_unrelated_decision_cannot_settle_surface(tmp_path):
    engine = make_engine(tmp_path)
    engine.findings['unrelated'] = {'source':{'file':'elsewhere.py'},'sink':{'file':'elsewhere.py'},'data_flow':[]}
    with pytest.raises(ValueError,match='unrelated evidence'):
        engine.dispatch('settle_surface',{'surface':'input','status':'reviewed','files':['a.py'],
            'reason':'Safe because another module was checked','assessment':'decision',
            'decision_ids':['unrelated'],'absence_evidence':[]})


def test_insufficient_evidence_requires_limitations_and_visible_report(tmp_path):
    engine = make_engine(tmp_path)
    engine.findings['h1'] = {'id':'h1','title':'Unresolved query','status':'INSUFFICIENT_EVIDENCE',
                            'source':{'file':'a.py'},'sink':{'file':'a.py'},'data_flow':[],
                            'judgment_scope':'conditional_code','deployment_exposure':'unknown'}
    reviews = [{'surface':surface,'status':'reviewed','files':['a.py'],'reason':'Unresolved hypothesis',
                'assessment':'decision','decision_ids':['h1'],'absence_evidence':[]} for surface in ('input','storage')]
    args = {'summary':'Investigation ended','limitations':[],'surface_reviews':reviews}
    with pytest.raises(ValueError,match='Insufficient evidence requires'):
        engine.dispatch('finish',args)
    engine.dispatch('finish',dict(args,limitations=['Query behavior unresolved']))
    assert engine.status == 'COMPLETE'  # Workflow completion is deliberately distinct.
    engine.report({'status':engine.status,'counts':{'INSUFFICIENT_EVIDENCE':1},'coverage':engine.coverage(),'completion':engine.completion})
    report = (engine.audit/'report.md').read_text()
    assert 'insufficient_evidence_ids' in report and 'h1' in report
    assert 'workflow_completion_is_not_safety' in report
    assert engine.assessment_summary()['deployment_exposure_unknown_ids'] == ['h1']


def test_truncated_read_line_cannot_support_feature_absence(tmp_path):
    engine = make_engine(tmp_path)
    engine.read_cache['a.py'][2] = 'print('
    review = {'surface':'storage','status':'reviewed','files':['a.py'],'reason':'No database',
              'assessment':'feature_absent','decision_ids':[],
              'absence_evidence':[{'file':'a.py','line':1,'symbol':'value','evidence':'value = input()'}]}
    with pytest.raises(ValueError,match='fully read'):
        engine.dispatch('settle_surface',review)


def test_unread_note_error_identifies_recovery_location(tmp_path):
    engine = make_engine(tmp_path)
    note = {'id':'n','summary':'Version unknown','references':[{'file':'pyproject.toml','line':3,
            'symbol':'version','evidence':'version = "3.0.5"'}], 'open_questions':[], 'next_action':'read version'}
    with pytest.raises(ValueError,match=r'pyproject.toml:3.*not read.*repo.read_range'):
        engine.dispatch('investigation_note',note)
    assert engine.notes == {}


def test_repeated_failed_notes_stop_before_iteration_budget(tmp_path):
    engine = make_engine(tmp_path)
    class RepeatingModel:
        model='offline-test-double'
        usage=[]
        calls=0
        def complete(self, messages, tools):
            self.calls += 1
            return {'role':'assistant','tool_calls':[{'id':str(self.calls),'type':'function','function':{
                'name':'investigation_note','arguments':json.dumps({'id':'n','summary':'Version unknown',
                'references':[{'file':'pyproject.toml','line':3,'symbol':'version','evidence':'version = "3.0.5"'}],
                'open_questions':[],'next_action':'read'})}}]}
    engine.model=RepeatingModel()
    result=engine.run()
    assert result['status']=='INCOMPLETE' and 'Repeated action failure' in result['failure']
    assert engine.model.calls==3 and engine.notes=={}
    events=[json.loads(line) for line in (engine.audit/'tool_calls.jsonl').read_text().splitlines()]
    assert events[-1]['result_summary']['consecutive_same_failure']==3
