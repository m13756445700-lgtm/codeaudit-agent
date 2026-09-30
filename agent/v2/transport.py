"""Real OctoBus MCP transport; local adapter is explicitly marked for unit runs."""
import json
import time
import urllib.request


class OctoBus:
    kind = 'octobus-mcp'

    def __init__(self, url, token, audit_id):
        self.url, self.token, self.audit_id = url, token, audit_id
        self.session = None
        self.counter = 0
        self.rpc('initialize', {'protocolVersion': '2025-03-26', 'capabilities': {},
                               'clientInfo': {'name': 'codeaudit-v2', 'version': '2.0'}})
        self.rpc('notifications/initialized', {}, notification=True)
        listing = self.rpc('tools/list', {})['tools']
        matches = [t for t in listing if t['name'].replace('_', '').lower().endswith('executetool')]
        if len(matches) != 1:
            raise ValueError('Expected one V2 ExecuteTool capability')
        self.tool = matches[0]

    def rpc(self, method, params, notification=False):
        self.counter += 1
        request = {'jsonrpc': '2.0', 'method': method, 'params': params}
        if not notification:
            request['id'] = self.counter
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream',
                   'Authorization': 'Bearer ' + self.token, 'MCP-Protocol-Version': '2025-03-26'}
        if self.session:
            headers['Mcp-Session-Id'] = self.session
        with urllib.request.urlopen(urllib.request.Request(self.url, json.dumps(request).encode(), headers), timeout=150) as response:
            self.session = response.headers.get('Mcp-Session-Id', self.session)
            raw = response.read(2 * 1024 * 1024).decode()
        if notification and not raw.strip():
            return {}
        if raw.lstrip().startswith('data:') or '\ndata:' in raw:
            values = [json.loads(line[5:].strip()) for line in raw.splitlines() if line.startswith('data:')]
            payload = next(v for v in values if v.get('id') == self.counter)
        else:
            payload = json.loads(raw)
        if 'error' in payload:
            raise ValueError('OctoBus RPC failed')
        return payload['result']

    def call(self, name, arguments):
        for attempt in range(4):
            result = self._call(name, arguments)
            error = result.get('error') if isinstance(result, dict) else 'INVALID_RESULT'
            if not error:
                return result
            if error in ('SERVICE_BUSY', 'CAPABILITY_HTTP_503') and attempt < 3:
                time.sleep(0.5 * (attempt + 1))
                continue
            allowed = {'SERVICE_BUSY', 'CAPABILITY_HTTP_503', 'CAPABILITY_HTTP_400', 'CAPABILITY_HTTP_502',
                       'OUTPUT_LIMIT', 'VALIDATION_TIMEOUT', 'WORKER_START_FAILED', 'CONTROLLED_METHOD_FAILED',
                       'INVALID_WORKER_RESPONSE', 'CAPABILITY_FAILED'}
            raise ValueError('Capability error: ' + (error if error in allowed else 'INVALID_RESULT'))

    def _call(self, name, arguments):
        properties = self.tool['inputSchema']['properties']
        field = 'requestJson' if 'requestJson' in properties else 'request_json'
        response = self.rpc('tools/call', {'name': self.tool['name'], 'arguments': {field: json.dumps(
            {'audit_id': self.audit_id, 'tool': name, 'arguments': arguments})}})
        if response.get('isError'):
            raise ValueError('Controlled capability failed')
        payload = response.get('structuredContent')
        if payload is None:
            payload = json.loads(next(c['text'] for c in response['content'] if c['type'] == 'text'))
        for key in ('resultJson', 'result_json'):
            if key in payload:
                return json.loads(payload[key])
        raise ValueError('Invalid capability response')


class Local:
    kind = 'local-development'

    def __init__(self, layer):
        self.layer = layer

    def call(self, name, arguments):
        return self.layer.call(name, arguments)
