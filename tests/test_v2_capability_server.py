import json
import threading
import urllib.request
import urllib.error

import pytest
from agent.v2.capability_server import execute, server
from agent.v2.repository import snapshot


@pytest.fixture
def audit(tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    (src / 'app.py').write_text('value = 1\n')
    directory, _ = snapshot(src, tmp_path / 'ws')
    return directory, {'audit_id': directory.name, 'tool': 'repo.read_file', 'arguments': {'path': 'app.py'}}


def test_service_boundary_and_path_rejection(audit):
    directory, request = audit
    assert execute(request, 'repo-tools', directory.parent)['lines'][0]['code'] == 'value = 1'
    with pytest.raises(ValueError):
        execute(request, 'static-analysis', directory.parent)
    with pytest.raises(ValueError):
        execute(dict(request, tool='static.semgrep'), 'repo-tools', directory.parent)
    with pytest.raises(ValueError):
        execute(dict(request, audit_id='../escape'), 'repo-tools', directory.parent)
    with pytest.raises(ValueError):
        execute(dict(request, arguments={'path': '../metadata.json'}), 'repo-tools', directory.parent)


def test_http_validation_and_real_read(audit):
    directory, request = audit
    http = server(('127.0.0.1', 0), 'repo-tools', directory.parent)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{http.server_port}'
    try:
        with urllib.request.urlopen(url + '/health') as response:
            assert json.load(response)['role'] == 'repo-tools'
        with urllib.request.urlopen(urllib.request.Request(url + '/execute', json.dumps(request).encode())) as response:
            assert json.load(response)['file'] == 'app.py'
        for body, status in [(b'not json', 400), (b'x' * 65537, 413), (b'[]', 400)]:
            with pytest.raises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(urllib.request.Request(url + '/execute', body))
            assert error.value.code == status
        with urllib.request.urlopen(url + '/health') as response:
            assert response.status == 200
    finally:
        http.shutdown()
        thread.join(timeout=5)
        http.server_close()


def test_deployment_isolates_worker_network_and_source():
    from pathlib import Path
    import yaml
    root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((root / 'docker-compose.yml').read_text())
    assert config['networks']['capabilities']['internal'] is True
    for name in ('repo-tools', 'static-analysis'):
        service = config['services'][name]
        assert service['networks'] == ['capabilities']
        assert not service.get('ports')
        assert service['read_only'] is True
        assert service['mem_limit'] and service['cpus'] and service['healthcheck']
    assert config['services']['repo-tools']['volumes'][0]['read_only'] is True
    project = yaml.safe_load((root / 'agent-compose.yml').read_text())
    assert project['agents']['auditor']['image'] == 'codeaudit-final:2.0'
    assert project['agents']['auditor']['env']['CODEAUDIT_LLM_API_KEY']['secret'] is True
