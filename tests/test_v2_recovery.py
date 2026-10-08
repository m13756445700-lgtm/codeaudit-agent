import json
import pytest
from agent.v2.engine import Engine
from agent.v2.recovery import NeedsMoreEvidence
from agent.v2.repository import snapshot, profile
from agent.v2.tools import ToolLayer
from agent.v2.transport import Local

class Script:
    model = 'scripted-not-real'
    usage = []
    def __init__(self, steps): self.steps = iter(steps)
    def complete(self, *_):
        name, args = next(self.steps)
        return {'role': 'assistant', 'content': None, 'tool_calls': [
            {'id': 'x', 'type': 'function', 'function': {'name': name, 'arguments': json.dumps(args)}}]}

def setup(tmp_path, lines=127):
    src=tmp_path/'src';src.mkdir();(src/'ledger.py').write_text('value = 1\n'*lines)
    audit,meta=snapshot(src,tmp_path/'audits')
    e=Engine(None,Local(ToolLayer(audit)),audit,meta,profile(audit/'repo'))
    e.dispatch('submit_plan', {'plan': {'attack_surfaces':['storage'], 'next_actions':['read']}})
    e.dispatch('use_tool', request(1,120))
    return e

def request(start,end):
    return {'tool':'repo.read_range','arguments':{'path':'ledger.py','start':start,'end':end},'purpose':'read missing scope'}

def review():
    return {'surface':'storage','status':'reviewed','files':['ledger.py'],'assessment':'feature_absent',
            'decision_ids':[],'absence_evidence':[{'file':'ledger.py','line':1,'symbol':'value','evidence':'value = 1'}],
            'reason':'No storage feature in this synthetic declared scope'}

def test_strict_machine_readable_and_manual_recovery(tmp_path):
    e=setup(tmp_path)
    with pytest.raises(NeedsMoreEvidence) as err:e.dispatch('settle_surface',review())
    state=err.value.feedback
    assert state['status']=='NEEDS_MORE_EVIDENCE'
    assert state['missing_files']==[{'path':'ledger.py','missing_ranges':[[121,127]],'blocked_reason':None}]
    assert not e.surface_settlements and not e.findings
    e.dispatch('use_tool',request(121,127))
    assert e.pending_evidence['storage']['status']=='READY_FOR_REASSESSMENT'
    assert not e.surface_settlements
    assert e.dispatch('settle_surface',review())['accepted']
    assert not e.pending_evidence and not e.findings

def test_no_progress_stops_despite_unrelated_success(tmp_path):
    e=setup(tmp_path)
    e.model=Script([('settle_surface',review()),('investigation_state',{}),('settle_surface',review()),('use_tool',request(1,120)),('settle_surface',review())])
    result=e.run()
    assert result['status']=='INCOMPLETE'
    assert 'without progress' in result['failure']
    assert e.pending_evidence['storage']['no_progress_failures']==3
    assert not e.findings

def test_progress_then_finish_is_not_killed(tmp_path):
    e=setup(tmp_path)
    e.model=Script([('settle_surface',review()),('use_tool',request(121,127)),('settle_surface',review()),
                    ('finish',{'summary':'Bounded synthetic scope','limitations':[],'surface_reviews':[]})])
    result=e.run()
    assert result['status']=='COMPLETE' and not e.findings
    assert e.recovery_history['storage']['resolution']=='reviewed'

def test_compaction_and_disk_keep_pending_gaps(tmp_path):
    e=setup(tmp_path)
    with pytest.raises(NeedsMoreEvidence):e.dispatch('settle_surface',review())
    e.messages.append({'role':'user','content':'x'*90000});e.compact_context()
    memory=json.loads(e.messages[2]['content'])
    assert memory['pending_evidence']['storage']['missing_files'][0]['missing_ranges']==[[121,127]]
    assert e.investigation_checkpoint(1)['priority']=='recover_missing_evidence'
    assert e.dispatch('investigation_state',{})['pending_evidence']
    assert json.loads((e.audit/'evidence_recovery.json').read_text())['pending_evidence']

@pytest.mark.parametrize('failure',['missing','changed','truncated','empty'])
def test_unavailable_evidence_never_complete(tmp_path,failure):
    e=setup(tmp_path)
    p=e.audit/'repo'/'ledger.py'
    p.chmod(0o600)  # Explicit test fault injection into a read-only snapshot.
    if failure=='missing':p.unlink()
    elif failure=='changed':p.write_text('changed\n')
    elif failure=='empty':
        p.write_text('');from agent.v2.repository import digest
        e.metadata['files']['ledger.py']=digest(p)
    else:
        p.write_text('value = 1\n'*120+'a'*2001+'\n');from agent.v2.repository import digest
        e.metadata['files']['ledger.py']=digest(p)
    e.model=Script([('settle_surface',review())]*3)
    result=e.run()
    assert result['status']=='INCOMPLETE' and not e.surface_settlements and not e.findings
    assert e.pending_evidence['storage']['missing_files'][0]['blocked_reason']

@pytest.mark.parametrize('budget',['round','calls'])
def test_budget_exhaustion_retains_missing_evidence(tmp_path,budget):
    e=setup(tmp_path);e.model=Script([('settle_surface',review())]*2)
    if budget=='round':e.max_iterations=1
    else:e.max_calls=1
    result=e.run()
    assert result['status']=='INCOMPLETE' and not e.findings
    assert e.pending_evidence['storage']['remaining_missing_evidence']

def test_recovery_attempt_budget_bounds_changing_arguments(tmp_path):
    e=setup(tmp_path);e.max_recovery_attempts=3
    e.model=Script([('settle_surface',dict(review(),reason='changed wording '+str(i))) for i in range(3)])
    result=e.run()
    assert 'recovery budget exhausted' in result['failure'] and result['status']=='INCOMPLETE'

def test_partial_progress_changes_failure_fingerprint(tmp_path):
    e=setup(tmp_path)
    with pytest.raises(NeedsMoreEvidence):e.dispatch('settle_surface',review())
    key=e.pending_evidence['storage']['fingerprint']
    e.dispatch('use_tool',request(121,123))
    with pytest.raises(NeedsMoreEvidence):e.dispatch('settle_surface',review())
    assert e.pending_evidence['storage']['fingerprint']!=key
    assert e.pending_evidence['storage']['no_progress_failures']==1
    assert e.pending_evidence['storage']['recovery_attempts']==2

def test_segment_boundary_requires_checkpoint_not_extra_budget(tmp_path):
    e=setup(tmp_path)
    for _ in range(11):e.dispatch('use_tool',request(1,120))
    with pytest.raises(NeedsMoreEvidence) as err:e.dispatch('settle_surface',review())
    assert err.value.feedback['recommended_actions'][0]['action']=='investigation_note'
    with pytest.raises(ValueError,match='segment exhausted'):e.dispatch('use_tool',request(121,127))
    e.dispatch('investigation_note',{'id':'recovery','summary':'Tail unread','references':review()['absence_evidence'],
                                    'open_questions':['Read missing tail'],'next_action':'Read121..127'})
    e.dispatch('use_tool',request(121,127));assert e.dispatch('settle_surface',review())['accepted']

def test_one_response_batch_counts_as_one_failed_round(tmp_path):
    e=setup(tmp_path)
    e._recovery_round=1
    for _ in range(3):
        with pytest.raises(NeedsMoreEvidence):e.dispatch('settle_surface',review())
    assert e.pending_evidence['storage']['no_progress_failures']==1
    assert e.pending_evidence['storage']['recovery_attempts']==1
