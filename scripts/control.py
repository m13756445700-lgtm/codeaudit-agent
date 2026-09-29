"""Portable single-operator deployment. Requires Python 3.9+ and Docker Compose v2."""
import json
import os
from pathlib import Path
import platform
import secrets
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)


def read_env(path):
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, sep, value = line.partition('=')
        if not sep or not key.replace('_', '').isalnum():
            raise SystemExit('Use simple KEY=value configuration: ' + str(path))
        values[key] = value.strip().strip('\"\'')
    return values


def run(command, capture=False, check=True, stdin=None):
    result = subprocess.run(command, text=True, input=stdin, capture_output=capture, check=False)
    if check and result.returncode:
        # Never echo command/stdin: commands may handle private credentials.
        raise SystemExit('Operation failed; inspect the preceding service output (exit %s)' % result.returncode)
    return result


def compose(*args, **kwargs):
    return run(['docker', 'compose', '--env-file', '.env', '--env-file', '.runtime.env', *args], **kwargs)


def bootstrap():
    config = read_env(ROOT/'.runtime.env')
    base = ['docker', 'compose', '--env-file', '.env', '--env-file', '.runtime.env', 'exec', '-T', 'octobus', 'octobus']
    def bus(*args, **kwargs):
        return run(base + list(args), capture=True, **kwargs)
    bus('service', 'import', 'codeaudit-repo-tools', '/opt/codeaudit/octobus/repo-tools')
    payload = json.dumps({'pythonPath':'/opt/codeaudit-venv/bin/python','applicationRoot':'/opt/codeaudit','workspaces':'/workspaces','repoEndpoint':'http://repo-tools:8080','staticEndpoint':'http://static-analysis:8080'})
    if bus('instance', 'get', 'codeaudit-v2-tools', check=False).returncode:
        bus('instance', 'create', 'codeaudit-v2-tools', '--service', 'codeaudit-repo-tools', '--config-json', payload)
    else:
        bus('instance', 'update-config', 'codeaudit-v2-tools', '--config-json', payload)
        bus('instance', 'restart', 'codeaudit-v2-tools')
    if bus('capset', 'get', 'codeaudit-v2', check=False).returncode:
        bus('capset', 'create', 'codeaudit-v2')
    members = json.loads(bus('capset', 'list-instances', 'codeaudit-v2').stdout).get('instances') or []
    if not any(item['InstanceID']=='codeaudit-v2-tools' for item in members):
        bus('capset', 'add-instance', 'codeaudit-v2', 'codeaudit-v2-tools')
    records = json.loads(bus('capset', 'list-tokens', 'codeaudit-v2').stdout)
    tokens = records.get('tokens') if isinstance(records, dict) else records
    if not tokens:
        bus('capset', 'add-token', 'codeaudit-v2', 'operator', '--token-stdin', stdin=config['CODEAUDIT_OCTOBUS_TOKEN'])
    # Deploy only operator-owned configuration. No target repository files enter daemon control paths.
    compose('exec', '-T', 'agent-compose', 'mkdir', '-p', '/data/work/codeaudit-final')
    for name in ['agent-compose.yml','.env','.runtime.env']:
        compose('cp', name, 'agent-compose:/data/work/codeaudit-final/'+name, capture=True)
    compose('exec', '-T', 'agent-compose', 'chmod', '600', '/data/work/codeaudit-final/.env','/data/work/codeaudit-final/.runtime.env')
    agent('config', '--quiet')
    agent('up')


def agent(*args):
    return compose('exec', '-T', 'agent-compose', 'agent-compose', '-f', '/data/work/codeaudit-final/agent-compose.yml', *args)


def start():
    if not (ROOT/'.env').exists():
        raise SystemExit('Copy .env.example to .env and supply LLM_API_KEY first.')
    env = read_env(ROOT/'.env')
    if not env.get('LLM_API_KEY') or env['LLM_API_KEY']=='your_api_key_here':
        raise SystemExit('Configure a real LLM_API_KEY in .env.')
    (ROOT/'.env').chmod(0o600)
    if not (ROOT/'.runtime.env').exists():
        project = env.get('COMPOSE_PROJECT_NAME', 'codeaudit-final')
        if not project or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in project):
            raise SystemExit('COMPOSE_PROJECT_NAME must use lowercase letters/digits/-/_.')
        volume = project+'-agent-data'
        run(['docker','volume','create',volume], capture=True)
        mount = run(['docker','volume','inspect',volume,'--format','{{.Mountpoint}}'],capture=True).stdout.strip()
        if platform.system()=='Linux':
            gateway = run(['docker','network','inspect','bridge','--format','{{(index .IPAM.Config 0).Gateway}}'],capture=True).stdout.strip()
            bind, host = gateway, gateway
        else:
            bind, host = '127.0.0.1', 'host.docker.internal'
        values = {'CODEAUDIT_BIND_ADDRESS':bind,'CODEAUDIT_SANDBOX_ROOT':mount+'/sandboxes',
                  'CODEAUDIT_RUNTIME_URL':'http://%s:%s'%(host,env.get('CODEAUDIT_DAEMON_PORT','17420')),
                  'CODEAUDIT_MCP_URL':'http://%s:%s/capsets/codeaudit-v2/mcp'%(host,env.get('CODEAUDIT_MCP_PORT','19013')),
                  'CODEAUDIT_OCTOBUS_TOKEN':secrets.token_hex(32),'CODEAUDIT_DAEMON_TOKEN':secrets.token_hex(32)}
        fd=os.open(ROOT/'.runtime.env',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as output: output.write(''.join(k+'='+v+'\n' for k,v in values.items()))
    compose('build','octobus')
    compose('up','-d','--wait','--wait-timeout','180','octobus','repo-tools','static-analysis','agent-compose')
    bootstrap()
    health()


def health():
    compose('ps')
    agent('status')
    # Check real MCP registration and authentication, not just process liveness.
    command = 'from agent.v2.transport import OctoBus; import os; t=OctoBus(os.environ["CODEAUDIT_MCP_URL"],os.environ["CODEAUDIT_OCTOBUS_TOKEN"],"healthcheck"); print("MCP registered:",t.tool["name"])'
    compose('run','--rm','--no-deps','--entrypoint','python','codeaudit-agent','-c',command)


def demo(kind):
    examples={'a':'/opt/codeaudit/benchmark/python-sql-raw', 'b':'/opt/codeaudit/benchmark/false-positive',
              'c':'/opt/codeaudit/benchmark/cross-file-flow',
              'd':'https://github.com/miguelgrinberg/flask-video-streaming.git'}
    source=examples.get(kind.lower(), kind)
    command=shlex.join(['/opt/codeaudit-venv/bin/python','/opt/codeaudit/scripts/run-agent.py',source,'--keep-source'])
    agent('run','auditor','--command',command)


def acceptance(mode):
    (ROOT/'runs').mkdir(exist_ok=True)
    compose('run','--rm','--entrypoint','python','-v',str(ROOT/'runs')+':/opt/codeaudit/runs','codeaudit-agent','scripts/v2_acceptance.py',mode)


if __name__=='__main__':
    action=sys.argv[1] if len(sys.argv)>1 else 'healthcheck'
    if action=='start': start()
    elif action=='healthcheck': health()
    elif action=='bootstrap': bootstrap()
    elif action=='demo': demo(sys.argv[2] if len(sys.argv)>2 else 'c')
    elif action in ('integration','ablation','benchmark'): acceptance(action)
    elif action=='stop':
        agent('down')
        compose('down')  # Deliberately preserve evidence volumes.
    else: raise SystemExit('Unknown action')
