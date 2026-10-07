import json
import pytest
from scripts import consolidated_acceptance as batch


def test_prepare_is_offline_and_freeze_detects_source_change(tmp_path, monkeypatch):
    import agent.v2.model
    monkeypatch.setattr(agent.v2.model, 'Model', lambda: pytest.fail('Offline preparation must not instantiate model'))
    output = tmp_path/'campaign'
    plan = batch.prepare(output, repeats=1)
    assert len(plan['jobs']) == 44
    assert batch.load_frozen(output)['implementation_sha256'] == plan['implementation_sha256']
    with pytest.raises(ValueError, match='exists'): batch.prepare(output)
    assert not batch.summarize(output)['release_ready']
    raw = json.loads((output/'plan.json').read_text()); raw['model'] = 'changed'
    (output/'plan.json').write_text(json.dumps(raw))
    with pytest.raises(ValueError, match='plan changed'): batch.load_frozen(output)


def test_http402_stops_entire_campaign_and_keeps_failed_attempt(tmp_path, monkeypatch):
    import agent.v2.model
    import agent.v2.transport
    class RefusedModel:
        model = 'deepseek-flash'
        usage = []
        def complete(self, *args):
            raise RuntimeError('Model HTTP error 402')
    class NoNetwork:
        kind = 'offline-test-double'
        def __init__(self, *args): pass
        def call(self, *args): pytest.fail('No capability expected after immediate model refusal')
    monkeypatch.setattr(agent.v2.model, 'Model', RefusedModel)
    monkeypatch.setattr(agent.v2.transport, 'OctoBus', NoNetwork)
    monkeypatch.setenv('CODEAUDIT_WORKSPACES', str(tmp_path/'ws'))
    monkeypatch.setenv('CODEAUDIT_MCP_URL', 'http://unused')
    monkeypatch.setenv('CODEAUDIT_OCTOBUS_TOKEN', 'test-only')
    output = tmp_path/'campaign'; batch.prepare(output, repeats=1)
    result = batch.run_live(output, max_runs=44)
    assert result['attempted_runs'] == 1 and result['complete_runs'] == 0
    assert json.loads((output/'STOPPED.json').read_text())['reason'].endswith('402')
    records = (output/'results.jsonl').read_text().splitlines()
    assert len(records) == 1 and json.loads(records[0])['summary']['status'] == 'INCOMPLETE'


def test_stopped_campaign_cannot_make_any_model_call(tmp_path, monkeypatch):
    import agent.v2.model
    monkeypatch.setattr(agent.v2.model, 'Model', lambda: pytest.fail('Must not instantiate model'))
    out = tmp_path/'campaign'; batch.prepare(out, repeats=1)
    (out/'STOPPED.json').write_text('{}')
    with pytest.raises(ValueError, match='Campaign stopped'):
        batch.run_live(out, 1)
    (out/'STOPPED.json').unlink()
    (out/'results.jsonl').write_text(json.dumps({'job_index':0,'summary':{'failure':'Model HTTP error 402'}})+'\n')
    with pytest.raises(ValueError, match='provider failure'):
        batch.run_live(out, 1)


@pytest.mark.parametrize('scope,focus,valid', [
    ('focused','Inspect file serving',True), ('full',None,True),
    ('focused',None,False), ('full','Hidden narrowing',False), ('focused',42,False)])
def test_frozen_job_focus_reaches_engine_without_labels(tmp_path, monkeypatch, scope, focus, valid):
    import hashlib
    import agent.v2.model
    import agent.v2.transport
    seen = []
    class ProbeModel:
        model = 'deepseek-flash'
        usage = []
        def complete(self, messages, tools):
            seen.append(messages)
            raise RuntimeError('Offline probe end')
    class NoNetwork:
        kind = 'offline-test-double'
        def __init__(self, *args): pass
        def call(self, *args): pytest.fail('No network expected')
    monkeypatch.setattr(agent.v2.model, 'Model', ProbeModel)
    monkeypatch.setattr(agent.v2.transport, 'OctoBus', NoNetwork)
    for key,value in {'CODEAUDIT_WORKSPACES':str(tmp_path/'ws'),'CODEAUDIT_MCP_URL':'http://unused','CODEAUDIT_OCTOBUS_TOKEN':'test-only'}.items():
        monkeypatch.setenv(key,value)
    out = tmp_path/'campaign'; plan = batch.prepare(out, repeats=1)
    plan['jobs'] = [dict(plan['jobs'][0], scope=scope, focus=focus)]
    plan['cases'][0]['target']['private_label'] = 'DO_NOT_SEND_TARGET_LABEL'
    plan['cases'][0]['policy'] = 'Only project owners may change billing.'
    raw = json.dumps(plan)
    (out/'plan.json').write_text(raw)
    (out/'plan.sha256').write_text(hashlib.sha256(raw.encode()).hexdigest())
    if not valid:
        with pytest.raises(ValueError, match='focus'):
            batch.run_live(out, 1)
        assert seen == []
        return
    batch.run_live(out, 1)
    context = json.loads(seen[0][1]['content'])
    assert context['operator_scope'] == (focus or 'Prioritize a bounded set of repository-specific risks within budget; clearly state unexamined scope.')
    assert context['operator_supplied_business_policy'] == 'Only project owners may change billing.'
    assert 'DO_NOT_SEND_TARGET_LABEL' not in json.dumps(seen)
    record = json.loads((out/'results.jsonl').read_text())
    assert record['scope'] == scope and record['focus'] == focus
