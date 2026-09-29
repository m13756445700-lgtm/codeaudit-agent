"""Fresh null lists and idempotent registration must preserve existing credentials."""
import importlib.util
import json
import subprocess
from pathlib import Path
import pytest


@pytest.mark.parametrize('existing', [False, True])
def test_bootstrap_handles_fresh_and_existing_capsets(monkeypatch, existing):
    spec=importlib.util.spec_from_file_location('control',Path(__file__).resolve().parents[1]/'scripts/control.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    calls=[]
    monkeypatch.setattr(module,'read_env',lambda p:{'CODEAUDIT_OCTOBUS_TOKEN':'test-only-placeholder-token'})
    def run(command, **kwargs):
        calls.append((command,kwargs)); code=1 if not existing and 'get' in command else 0
        output=''
        if 'list-instances' in command: output=json.dumps({'instances':[{'InstanceID':'codeaudit-v2-tools'}] if existing else None})
        if 'list-tokens' in command: output=json.dumps({'tokens':[{'name':'operator'}] if existing else None})
        return subprocess.CompletedProcess(command,code,output,'')
    monkeypatch.setattr(module,'run',run)
    module.bootstrap()
    assert sum('add-instance' in c for c,_ in calls)==(0 if existing else 1)
    additions=[(c,k) for c,k in calls if 'add-token' in c]
    assert len(additions)==(0 if existing else 1)
    if additions:
        command,kwargs=additions[0]
        assert '--token-stdin' in command and kwargs['stdin'] not in command
