import json
import subprocess
import sys
from pathlib import Path

import pytest
from agent.v2.engine import Engine
from agent.v2.repository import snapshot, profile
from agent.v2.tools import ToolLayer
from agent.v2.transport import Local
from agent.v2.static_baseline import evaluate


def test_direct_repository_entry_requires_real_model(monkeypatch, tmp_path):
    monkeypatch.delenv('LLM_API_KEY', raising=False)
    result = subprocess.run([sys.executable, '-m', 'agent.cli', str(tmp_path)], capture_output=True, text=True)
    assert result.returncode != 0
    assert 'credential required' in result.stderr
    assert 'invalid choice' not in result.stderr


def test_coverage_uses_reads_not_completion_claim(tmp_path):
    src = tmp_path / 'src'; src.mkdir()
    (src / 'a.py').write_text('x = 1\ny = 2\n')
    (src / 'b.py').write_text('secret_flow = input()\n')
    audit, metadata = snapshot(src, tmp_path / 'ws')
    layer = ToolLayer(audit)
    engine = Engine(None, Local(layer), audit, metadata, profile(audit/'repo'))
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces': ['input'], 'next_actions': ['read']}})
    engine.dispatch('use_tool', {'tool': 'repo.read_range', 'arguments': {'path': 'a.py', 'start': 1, 'end': 1}, 'purpose': 'read'})
    with pytest.raises(ValueError): engine.dispatch('finish', {'summary': 'all safe'})
    with pytest.raises(ValueError, match='surface_reviews'):
        engine.dispatch('finish', {'summary': 'all safe', 'limitations': []})
    engine.dispatch('finish', {'summary': 'Limited investigation', 'limitations': ['Input surface not investigated'],
        'surface_reviews': [{'surface': 'input', 'status': 'deferred', 'files': [], 'reason': 'Budget ended before b.py'}]})
    assert engine.status == 'PARTIAL'
    coverage = engine.coverage()
    assert coverage['files_read'] == 1 and coverage['files_total'] == 2
    assert coverage['distinct_lines_read'] == 1
    assert coverage['unread_files'] == ['b.py']


def test_static_baseline_does_not_zero_existing_verdicts(monkeypatch, tmp_path):
    import agent.v2.static_baseline as baseline
    monkeypatch.setattr(baseline, 'analyze_candidate', lambda *a: {'sink': {'file': 'a.java', 'line': 1}})
    monkeypatch.setattr(baseline, 'finalize_finding', lambda *a: {'status': 'VERIFIED', 'recommendation': 'keep actual static output'})
    output = evaluate(tmp_path, {'snapshot_sha256': 'a'*64}, [{'rule_id': 'existing-rule'}])
    assert output['confirmed'] == output['security_verdicts'] == 1
    assert output['findings'][0]['recommendation'] == 'keep actual static output'


def test_gate_rejects_untyped_security_claims(tmp_path):
    from agent.v2.gate import validate
    result = validate({'status': 'CONFIRMED', 'confidence': {'fake': True},
                       'counter_evidence': 'I checked everything'}, tmp_path,
                      {'snapshot_sha256': '0'*64, 'files': {}}, [], {})
    assert result['status'] == 'INSUFFICIENT_EVIDENCE'
    assert 'missing:confidence' in result['evidence_gate']['problems']
    assert 'invalid:counter_evidence' in result['evidence_gate']['problems']


def test_decision_schema_requires_structured_counter_evidence():
    from agent.v2.engine import DECISION
    assert DECISION['properties']['counter_evidence']['items']['type'] == 'object'
    assert 'unknowns' in DECISION['required']


def test_gate_error_identifies_reference_location(tmp_path):
    from agent.v2.gate import validate
    result = validate({'status': 'LIKELY', 'data_flow': [], 'counter_evidence': ['unsupported text']},
                      tmp_path, {'snapshot_sha256': '0'*64, 'files': {}}, [], {})
    assert 'reference:counter_evidence[0]:missing reference' in result['evidence_gate']['problems']


def test_static_snapshot_adapter_retains_real_v1_verified_and_detects_tamper(tmp_path):
    audit, metadata = snapshot(Path(__file__).resolve().parents[1] / 'fixtures/spring-security-lab', tmp_path/'ws')
    repo = audit/'repo'
    signal = {'file': 'src/main/resources/mapper/UserMapper.xml', 'line': 5, 'rule_id': 'mybatis-raw-substitution'}
    output = evaluate(repo, metadata, [signal])
    assert not output['errors']
    assert output['findings'][0]['status'] == 'VERIFIED'
    assert output['findings'][0]['evidence_integrity']['status'] == 'PASS'
    target = repo/signal['file']
    target.chmod(0o600)
    target.write_text(target.read_text() + '\n<!-- changed -->\n')
    changed = evaluate(repo, metadata, [signal])
    assert changed['findings'][0]['status'] == 'NEEDS_REVIEW'
    assert changed['findings'][0]['evidence_integrity']['status'] == 'FAIL'


def test_completion_cannot_drop_surfaces_or_cite_unread_files(tmp_path):
    src = tmp_path / 'src'; src.mkdir()
    (src / 'a.py').write_text('x = 1\n')
    (src / 'b.py').write_text('eval(input())\n')
    audit, metadata = snapshot(src, tmp_path / 'ws')
    engine = Engine(None, Local(ToolLayer(audit)), audit, metadata, profile(audit/'repo'))
    for surfaces in (['entry', 'execution'], ['entry']):
        engine.dispatch('submit_plan', {'plan': {'attack_surfaces': surfaces, 'next_actions': ['read']}})
    engine.dispatch('use_tool', {'tool': 'repo.read_file', 'arguments': {'path': 'a.py'}, 'purpose': 'inspect'})
    reviews = [{'surface': 'entry', 'status': 'reviewed', 'files': ['a.py'], 'reason': 'Read entry'}]
    with pytest.raises(ValueError, match='Unsettled'):
        engine.dispatch('finish', {'summary': 'done', 'limitations': [], 'surface_reviews': reviews})
    reviews.append({'surface': 'execution', 'status': 'reviewed', 'files': ['b.py'], 'reason': 'claimed'})
    with pytest.raises(ValueError, match='actually read'):
        engine.dispatch('finish', {'summary': 'done', 'limitations': [], 'surface_reviews': reviews})
    assert not engine.finished


def test_decision_requires_knowledge_application_before_gate(tmp_path):
    src = tmp_path / 'src'; src.mkdir()
    (src / 'a.py').write_text('x = 1\n')
    audit, metadata = snapshot(src, tmp_path / 'ws')
    engine = Engine(None, Local(ToolLayer(audit)), audit, metadata, profile(audit/'repo'))
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces': ['entry'], 'next_actions': ['read']}})
    engine.dispatch('hypothesis', {'hypothesis': {'id': 'h1', 'statement': 'check', 'status': 'NEW'}})
    with pytest.raises(ValueError, match='Explain how knowledge'):
        engine.dispatch('submit_decision', {'finding': {'id': 'h1'}})
    with pytest.raises(ValueError, match='Retrieve relevant knowledge'):
        engine.dispatch('submit_decision', {'finding': {'id': 'h1', 'knowledge_application': 'not consulted'}})


def test_context_compaction_preserves_tool_pairs_and_audit_state(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'a.py').write_text('x = 1\n')
    audit, metadata = snapshot(src, tmp_path/'ws')
    engine = Engine(None, Local(ToolLayer(audit)), audit, metadata, profile(audit/'repo'))
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces': ['input'], 'next_actions': ['read']}})
    for i in range(8):
        engine.messages.extend([{'role': 'assistant', 'tool_calls': [{'id': str(i), 'function': {'name': 'use_tool', 'arguments': '{}'}}]},
                                {'role': 'tool', 'tool_call_id': str(i), 'content': 'a'*18000}])
    engine.compact_context()
    assert len(json.dumps(engine.messages)) < 85000
    assert 'all_planned_surfaces' in engine.messages[2]['content']
    assert [m['tool_call_id'] for m in engine.messages if m['role'] == 'tool'] == ['6', '7']
    assert 'context.compact' in (audit/'tool_calls.jsonl').read_text()


def test_oversized_model_read_gets_actionable_feedback_before_transport(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'a.py').write_text('x = 1\n')
    audit, metadata = snapshot(src, tmp_path/'ws')
    engine = Engine(None, None, audit, metadata, profile(audit/'repo'))
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces': ['input'], 'next_actions': ['read']}})
    with pytest.raises(ValueError, match='120 existing lines'):
        engine.dispatch('use_tool', {'tool': 'repo.read_range', 'arguments': {'path': 'a.py', 'start': 1, 'end': 300}, 'purpose': 'inspect'})


def test_compaction_retains_deduplicated_literal_read_evidence(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'a.py').write_text('danger = input()\neval(danger)\n')
    audit, metadata = snapshot(src, tmp_path/'ws')
    engine = Engine(None, Local(ToolLayer(audit)), audit, metadata, profile(audit/'repo'))
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces': ['input'], 'next_actions': ['read']}})
    for _ in range(2):
        engine.dispatch('use_tool', {'tool':'repo.read_file','arguments':{'path':'a.py'},'purpose':'inspect'})
    engine.messages.append({'role':'user','content':'x'*90000})
    engine.compact_context()
    memory = json.loads(engine.messages[2]['content'])
    assert memory['literal_read_excerpts']['a.py'] == '1: danger = input()\n2: eval(danger)\n'
    assert len(engine.receipts) == 2


def test_known_eof_feedback_survives_compaction(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'a.py').write_text('x = 1\nx = 2\n')
    audit, metadata = snapshot(src, tmp_path/'ws')
    engine = Engine(None, Local(ToolLayer(audit)), audit, metadata, profile(audit/'repo'))
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces': ['input'], 'next_actions': ['read']}})
    engine.dispatch('use_tool', {'tool': 'repo.read_file', 'arguments': {'path': 'a.py'}, 'purpose': 'inspect'})
    engine.messages.append({'role': 'user', 'content': 'x'*90000})
    engine.compact_context()
    assert json.loads(engine.messages[2]['content'])['file_lengths']['a.py'] == 2
    engine.transport = None  # Bad range must not reach the remote capability.
    with pytest.raises(ValueError, match='has 2 lines'):
        engine.dispatch('use_tool', {'tool': 'repo.read_range', 'arguments': {'path': 'a.py', 'start': 2, 'end': 4}, 'purpose': 'inspect'})


def test_checkpoint_replaces_stale_state_and_preserves_model_authority(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'a.py').write_text('x = 1\n')
    audit, metadata = snapshot(src, tmp_path/'ws')
    engine = Engine(None, Local(ToolLayer(audit)), audit, metadata, profile(audit/'repo'))
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces': ['input'], 'next_actions': ['read']}})
    engine.dispatch('hypothesis', {'hypothesis': {'id': 'H1', 'statement': 'Check input', 'status': 'NEW'}})
    assert engine.investigation_checkpoint(0)['priority'] == 'investigate'
    engine.hypotheses['H1']['status'] = 'REJECTED'
    engine.findings['H1'] = {'id': 'H1', 'status': 'REJECTED', 'evidence_gate': {'passed': True, 'problems': []}}
    state = engine.investigation_checkpoint(32)
    assert state['priority'] == 'settle'
    assert state['hypotheses'] == {'H1': 'REJECTED'}
    assert state['decisions']['H1']['gate_passed']
    assert len([m for m in engine.messages if m.get('content', '').startswith('CODEAUDIT_EXECUTION_STATE\n')]) == 1
    assert not engine.finished
    assert engine.findings['H1']['status'] == 'REJECTED'
    engine.messages.append({'role': 'user', 'content': 'x'*90000})
    engine.compact_context()
    assert engine.investigation_checkpoint(33)['hypotheses'] == {'H1': 'REJECTED'}


def test_unregistered_decision_feedback_keeps_hypothesis_requirement(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'a.py').write_text('x = 1\n')
    audit, metadata = snapshot(src, tmp_path/'ws')
    engine = Engine(None, Local(ToolLayer(audit)), audit, metadata, profile(audit/'repo'))
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces': ['input'], 'next_actions': ['read']}})
    with pytest.raises(ValueError, match='exact id'):
        engine.dispatch('submit_decision', {'finding': {'id': 'missing-id'}})
    assert not engine.hypotheses and not engine.findings


def test_first_read_over_eof_returns_bounds_without_evidence(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'a.py').write_text('x = 1\n')
    audit, metadata = snapshot(src, tmp_path/'ws')
    engine = Engine(None, Local(ToolLayer(audit)), audit, metadata, profile(audit/'repo'))
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces': ['input'], 'next_actions': ['read']}})
    result = engine.dispatch('use_tool', {'tool': 'repo.read_range', 'arguments': {'path': 'a.py', 'start': 1, 'end': 120}, 'purpose': 'inspect'})
    assert result['read_error'] == 'RANGE_OUTSIDE_FILE' and result['total_lines'] == 1
    assert not engine.receipts and not engine.read_cache
    assert engine.file_lengths['a.py'] == 1
    result = engine.dispatch('use_tool', {'tool': 'repo.read_range', 'arguments': {'path': 'a.py', 'start': 1, 'end': 1}, 'purpose': 'corrected read'})
    assert result['lines'][0]['code'] == 'x = 1'


def test_compaction_accounts_for_escaped_literal_evidence(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'a.py').write_text('x = 1\n')
    audit, metadata = snapshot(src, tmp_path/'ws')
    engine = Engine(None, Local(ToolLayer(audit)), audit, metadata, profile(audit/'repo'))
    engine.read_cache = {'a.py': {i: '\\"'*400 for i in range(1, 100)}}
    engine.messages.append({'role': 'user', 'content': 'x'*90000})
    engine.compact_context()
    assert len(json.dumps(engine.messages)) <= 85000
    assert engine.read_cache['a.py'][99] == '\\"'*400


def test_compaction_keeps_retrieved_knowledge_caveats_verbatim(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'a.py').write_text('x = 1\n')
    audit, metadata = snapshot(src, tmp_path/'ws')
    knowledge = tmp_path/'knowledge'; knowledge.mkdir()
    content = 'Fact: platform-specific behavior.\n' + 'context\n'*900 + 'LIMIT: exact versions only; no deployment proof.'
    (knowledge/'path_traversal.md').write_text(content)
    engine = Engine(None, Local(ToolLayer(audit, knowledge=knowledge)), audit, metadata, profile(audit/'repo'))
    engine.dispatch('submit_plan', {'plan': {'attack_surfaces': ['input'], 'next_actions': ['read']}})
    received = engine.dispatch('use_tool', {'tool': 'knowledge.retrieve', 'arguments': {'category': 'path_traversal'}, 'purpose': 'runtime semantics'})
    engine.messages.append({'role': 'user', 'content': 'x'*90000})
    engine.compact_context()
    memory = json.loads(engine.messages[2]['content'])
    assert memory['knowledge_documents']['path_traversal.md'] == received
    assert memory['knowledge_documents']['path_traversal.md']['content'].endswith('no deployment proof.')
    assert engine.findings == {}
    assert len(json.dumps(engine.messages)) <= 85000


def test_compaction_omits_whole_knowledge_payloads_with_explicit_retrieval_notice(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'a.py').write_text('x = 1\n')
    audit, metadata = snapshot(src, tmp_path/'ws')
    engine = Engine(None, None, audit, metadata, profile(audit/'repo'))
    for index in range(4):
        key = f'card{index}'
        engine.knowledge[key] = f'hash{index}'
        engine.knowledge_cache[key] = {'id': key, 'sha256': f'hash{index}', 'content': '\\"'*5000}
    engine.messages.append({'role': 'user', 'content': 'x'*90000})
    engine.compact_context()
    memory = json.loads(engine.messages[2]['content'])
    assert list(memory['knowledge_documents']) == ['card3']
    assert memory['knowledge_documents']['card3'] == engine.knowledge_cache['card3']
    assert len(memory['retrieved_knowledge']) == 4
    assert 'knowledge.retrieve' in memory['knowledge_notice']
    assert len(json.dumps(engine.messages)) <= 85000
