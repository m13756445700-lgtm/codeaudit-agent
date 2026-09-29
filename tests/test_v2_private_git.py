"""Real Git HTTP authentication against a local protected repository, no LLM needed."""
import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

import pytest
from agent.v2.repository import snapshot


def test_private_git_header_credentials(tmp_path, monkeypatch):
    source = tmp_path / 'source'
    source.mkdir()
    (source / 'app.py').write_text('value = 1\n')
    def git(*args):
        return subprocess.check_output(['git', *args], stderr=subprocess.DEVNULL)
    git('init', str(source))
    git('-C', str(source), 'add', '.')
    git('-C', str(source), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'fixture')
    git('clone', '--bare', str(source), str(tmp_path / 'private.git'))
    backend = git('--exec-path').decode().strip() + '/git-http-backend'
    credential = 'Bearer private-test-only-value'
    authenticated = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_GET(self):
            self.serve_git()
        def do_POST(self):
            self.serve_git()
        def serve_git(self):
            if self.headers.get('Authorization') != credential:
                self.send_response(401)
                self.send_header('WWW-Authenticate', 'Basic realm="fixture"')
                self.end_headers()
                return
            authenticated.append(self.path)
            url = urlsplit(self.path)
            env = dict(os.environ, GIT_PROJECT_ROOT=str(tmp_path), GIT_HTTP_EXPORT_ALL='1',
                       PATH_INFO=url.path, QUERY_STRING=url.query, REQUEST_METHOD=self.command,
                       CONTENT_TYPE=self.headers.get('Content-Type', ''),
                       CONTENT_LENGTH=self.headers.get('Content-Length', '0'))
            raw = subprocess.check_output([backend], env=env,
                        input=self.rfile.read(int(env['CONTENT_LENGTH'])))
            headers, body = raw.split(b'\r\n\r\n', 1)
            self.send_response(200)
            for line in headers.decode().split('\r\n'):
                name, value = line.split(':', 1)
                if name.lower() != 'status':
                    self.send_header(name, value.strip())
            self.end_headers()
            self.wfile.write(body)

    server = HTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}/private.git'
    monkeypatch.setenv('GIT_CONFIG_COUNT', '1')
    monkeypatch.setenv('GIT_CONFIG_KEY_0', f'http.{url}.extraHeader')
    monkeypatch.setenv('GIT_CONFIG_VALUE_0', 'Authorization: wrong')
    try:
        with pytest.raises((ValueError, subprocess.CalledProcessError)):
            snapshot(url, tmp_path / 'failed')
        assert not list((tmp_path / 'failed').iterdir())
        monkeypatch.setenv('GIT_CONFIG_VALUE_0', 'Authorization: ' + credential)
        audit, metadata = snapshot(url, tmp_path / 'success')
        assert authenticated
        assert metadata['input_kind'] == 'git'
        assert (audit / 'repo/app.py').read_text() == 'value = 1\n'
        from agent.v2.tools import ToolLayer
        change = ToolLayer(audit).call('repo.get_diff', {})
        assert change['available'] and '+value = 1' in change['patch']
        diff_path = audit / 'revision_diff.json'
        diff_path.chmod(0o600)
        diff_path.write_text('{}')
        with pytest.raises(ValueError, match='integrity'):
            ToolLayer(audit).call('repo.get_diff', {})
        assert credential not in json.dumps(metadata)
        assert metadata['commit'] == git('-C', str(source), 'rev-parse', 'HEAD').decode().strip()
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
