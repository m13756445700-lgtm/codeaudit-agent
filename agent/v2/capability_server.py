"""Internal, single-flight capability workers; never expose ports outside Docker."""
import argparse
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from agent.v2.repository import safe_path
from agent.v2.tools import NAMES, ToolLayer

MAX_BODY = 65536
MAX_OUTPUT = 1048576


def execute(request, role, workspaces):
    if not isinstance(request, dict) or set(request) != {'audit_id', 'tool', 'arguments'}:
        raise ValueError('Invalid request')
    name = request['tool']
    allowed = {'static.semgrep'} if role == 'static-analysis' else set(NAMES) - {'static.semgrep'}
    if not isinstance(name, str) or name not in allowed:
        raise ValueError('Capability not allowed by this service')
    audit_id = request['audit_id']
    if not isinstance(audit_id, str) or not re.fullmatch('[a-f0-9]{32}', audit_id):
        raise ValueError('Invalid audit id')
    return ToolLayer(safe_path(Path(workspaces), audit_id)).call(name, request['arguments'])


def server(address, role, workspaces):
    if role not in ('repo-tools', 'static-analysis'):
        raise ValueError('Invalid service role')
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def log_message(self, *args):
            pass  # Source and request contents must not appear in access logs.

        def reply(self, status, body):
            data = json.dumps(body).encode()
            if len(data) > MAX_OUTPUT:
                status, data = 502, b'{"error":"OUTPUT_LIMIT"}'
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path != '/health':
                return self.reply(404, {'error': 'NOT_FOUND'})
            self.reply(200, {'status': 'healthy', 'role': role})

        def do_POST(self):
            if self.path != '/execute':
                return self.reply(404, {'error': 'NOT_FOUND'})
            if self.headers.get('Transfer-Encoding'):
                return self.reply(400, {'error': 'INVALID_FRAMING'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                return self.reply(400, {'error': 'INVALID_LENGTH'})
            if not 0 < size <= MAX_BODY:
                return self.reply(413, {'error': 'BODY_LIMIT'})
            if not lock.acquire(blocking=False):
                return self.reply(503, {'error': 'SERVICE_BUSY'})
            try:
                body = self.rfile.read(size)
                if len(body) != size:
                    raise ValueError('Truncated request')
                result = execute(json.loads(body), role, workspaces)
                self.reply(200, result)
            except (ValueError, KeyError, TypeError, OSError):
                self.reply(400, {'error': 'INVALID_CAPABILITY_REQUEST'})
            except Exception:
                self.reply(502, {'error': 'CAPABILITY_FAILED'})
            finally:
                lock.release()

    return ThreadingHTTPServer(address, Handler)


def main():
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument('role', choices=['repo-tools', 'static-analysis'])
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    server(('0.0.0.0', args.port), args.role, os.environ['CODEAUDIT_WORKSPACES']).serve_forever()


if __name__ == '__main__':
    main()
