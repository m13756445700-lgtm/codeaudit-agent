"""OpenAI-compatible chat tool protocol. No static or mock fallback."""
import json
import os
import urllib.request
import urllib.error


class Model:
    def __init__(self):
        self.endpoint = os.environ.get('LLM_API_ENDPOINT', '').rstrip('/')
        self.key = os.environ.get('LLM_API_KEY', '')
        self.model = os.environ.get('CODEAUDIT_MODEL') or os.environ.get('LLM_MODEL') or 'deepseek-flash'
        if not self.endpoint or not self.key:
            raise ValueError('Model endpoint and credential required; no static verdict fallback')
        if not self.endpoint.startswith(('https://', 'http://127.0.0.1:', 'http://localhost:')):
            raise ValueError('Model endpoint must use HTTPS or local loopback')
        self.usage = []

    def complete(self, messages, tools):
        payload = {'model': self.model, 'messages': messages, 'tools': tools, 'tool_choice': 'auto',
                   'stream': False, 'max_tokens': 3500, 'temperature': 0}
        if 'deepseek' in self.model:
            payload['thinking'] = {'type': 'disabled'}
        request = urllib.request.Request(self.endpoint + '/chat/completions', json.dumps(payload).encode(),
                                        {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.key})
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                raw = response.read(2 * 1024 * 1024)
            data = json.loads(raw)
            message = data['choices'][0]['message']
            self.usage.append(data.get('usage', {}))
            # Deliberately discard reasoning_content/private chain of thought.
            return {k: message[k] for k in ('role', 'content', 'tool_calls') if k in message}
        except urllib.error.HTTPError as error:
            raise RuntimeError('Model HTTP error ' + str(error.code)) from None


def function(name, description, properties, required):
    return {'type': 'function', 'function': {'name': name, 'description': description, 'parameters': {
        'type': 'object', 'properties': properties, 'required': required, 'additionalProperties': False}}}
