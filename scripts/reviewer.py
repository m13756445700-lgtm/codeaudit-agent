#!/usr/bin/python3 -I
"""Install root-owned as /usr/local/bin/codeaudit-review; narrowly scoped sudo entry."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

ROOT = Path('/opt/codeaudit-v2')
os.chdir(ROOT)
os.environ.clear()
os.environ.update(PATH='/usr/sbin:/usr/bin:/sbin:/bin', HOME='/root', LANG='C.UTF-8')
COMPOSE = ['/usr/bin/docker', 'compose', '--env-file', '.env', '--env-file', '.runtime.env']
AGENT = COMPOSE + ['exec', '-T', 'agent-compose', 'agent-compose', '-f', '/data/work/codeaudit-final/agent-compose.yml']

def run(argv, capture=False):
    return subprocess.run(argv, check=True, text=True, capture_output=capture, timeout=1020)


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit('Usage: sudo codeaudit-review status|projects|triggers|runs|methods|trigger|audit HTTPS_URL|report [AUDIT_ID]|trace AUDIT_ID')
    action = args[0]
    commands = {'status': COMPOSE + ['ps'], 'projects': AGENT + ['project', 'ls'],
                'triggers': AGENT + ['scheduler', 'ls'], 'runs': AGENT + ['scheduler', 'runs', '--limit', '10'],
                'methods': COMPOSE + ['exec', '-T', 'octobus', 'octobus', 'capset', 'list-methods', 'codeaudit-v2'],
                'trigger': AGENT + ['scheduler', 'trigger', 'auditor', 'daily-v2-audit']}
    if action in commands and len(args) == 1:
        run(commands[action]); return
    if action == 'audit' and len(args) == 2:
        url = urlsplit(args[1])
        # Public GitHub is a deliberately bounded reviewer convenience entry.
        if url.scheme != 'https' or url.netloc != 'github.com' or url.query or url.fragment or not re.fullmatch(r'/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?', url.path):
            raise SystemExit('Use a public https://github.com/owner/repository URL; other inputs require the documented operator CLI.')
        import shlex
        run(AGENT + ['run', 'auditor', '--command', shlex.join(['/opt/codeaudit-venv/bin/python', '/opt/codeaudit/scripts/run-agent.py', args[1], '--keep-source'])]); return
    if (action == 'report' and len(args) in (1, 2)) or (action == 'trace' and len(args) == 2):
        volume = json.loads(run(COMPOSE + ['config', '--format', 'json'], True).stdout)['volumes']['agent-data']['name']
        mount = Path(run(['/usr/bin/docker', 'volume', 'inspect', volume, '--format', '{{.Mountpoint}}'], True).stdout.strip())
        base = mount/'sandboxes/codeaudit-v2-workspaces'
        candidates = [p for p in base.iterdir() if re.fullmatch('[a-f0-9]{32}', p.name) and not p.is_symlink() and (p/'run_summary.json').is_file()]
        if len(args) == 2:
            candidates = [p for p in candidates if p.name == args[1]]
        if not candidates:
            raise SystemExit('No matching completed/partial audit output')
        audit = max(candidates, key=lambda p: (p/'run_summary.json').stat().st_mtime)
        for name in (['tool_calls.jsonl', 'knowledge_used.json'] if action == 'trace' else ['run_summary.json', 'report.md', 'audit_plan.json', 'surface_reviews.json']):
            path = audit/name
            if path.is_file() and not path.is_symlink():
                print('\n--- ' + audit.name + '/' + name + ' ---\n' + path.read_text()[:60000])
        return
    raise SystemExit('Invalid command or arguments')

if __name__ == '__main__':
    main()
