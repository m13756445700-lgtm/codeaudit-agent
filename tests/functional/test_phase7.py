import subprocess
import sys
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[2]

def test_project_contract():
    project = yaml.safe_load((ROOT/'agent-compose.yml').read_text())
    agent = project['agents']['auditor']
    assert agent['provider'] == 'codex'
    assert agent['mcp_servers'] == ['octobus']
    assert not agent.get('volumes')
    assert project['mcp_servers']['octobus']['headers']['Authorization']['secret'] is True

def test_patch_is_all_or_nothing(tmp_path):
    p = tmp_path/'codex.js'
    p.write_text('sandboxMode: "danger-full-access"')
    old = p.read_bytes()
    run = subprocess.run([sys.executable,str(ROOT/'deploy/guest/harden-runtime.py'),str(p)], capture_output=True)
    assert run.returncode != 0
    assert p.read_bytes() == old

def test_patch_expected_runner_contract(tmp_path):
    p = tmp_path/'codex.js'
    p.write_text('sandboxMode: "danger-full-access", networkAccessEnabled: true, config: { developer_instructions: this.options.systemContext }')
    subprocess.run([sys.executable,str(ROOT/'deploy/guest/harden-runtime.py'),str(p)],check=True)
    result = p.read_text()
    assert 'sandboxMode: "read-only"' in result
    assert 'networkAccessEnabled: false' in result
    assert '"features.shell_tool": false' in result

def test_model_cannot_override_saved_verdict(tmp_path):
    import json
    import pytest
    from agent.workflow.validation import verify_output, structured_output, OutputError
    run_id = 'a'*32
    folder = tmp_path/run_id
    folder.mkdir()
    finding = {'status':'NEEDS_REVIEW'}
    (folder/'validation-result.json').write_text(json.dumps({'repository':'lab','commit':'b'*40,'finding':finding}))
    value = {'repository':'lab','commit':'b'*40,'validation_run_ids':[run_id],'findings':[finding]}
    assert verify_output(json.dumps(value),tmp_path) == value
    value['findings'] = [{'status':'VERIFIED'}]
    with pytest.raises(OutputError):
        verify_output(json.dumps(value),tmp_path)
    calls=[]
    def generate(attempt):
        calls.append(attempt)
        return 'invalid'
    with pytest.raises(OutputError,match='RETRIES_EXHAUSTED'):
        structured_output(generate,tmp_path)
    assert calls == [0,1]
