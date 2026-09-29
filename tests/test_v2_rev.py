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
    engine.dispatch('finish', {'summary': 'all safe', 'limitations': []})
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
