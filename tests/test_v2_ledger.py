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
    engine.dispatch('settle_surface', {'surface':'input', 'status':'reviewed', 'files':['a.py'], 'reason':'Read input/output path'})
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
    review = {'surface':'input','status':'reviewed','files':['a.py'],'reason':'Input read'}
    engine.dispatch('settle_surface', review)
    result = engine.dispatch('settle_surface', review)
    assert result['unchanged'] and result['remaining'] == ['storage']
    assert engine.segment_calls == 1 and not engine.finished
