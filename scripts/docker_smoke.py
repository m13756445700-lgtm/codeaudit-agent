"""No model/network calls. Start only ephemeral local test containers and clean them."""
import subprocess,sys,time,uuid,json
image=sys.argv[1];created=[]
def run(args):
    r=subprocess.run(['docker',*args],capture_output=True,text=True,timeout=30)
    print(json.dumps({'command':['docker',*args],'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}),flush=True)
    if r.returncode:raise RuntimeError('Docker smoke command failed')
    return r.stdout.strip()
try:
    run(['run','--rm','--network','none',image,'python','-c','import agent.v2.engine, agent.v2.capability_server; print("application import OK")'])
    run(['run','--rm','--network','none',image,'codeaudit','--help'])
    for service in ('repo-tools','static-analysis','octobus'):
        name='codeaudit-smoke-'+uuid.uuid4().hex[:12];created.append(name)
        command=['octobus','serve'] if service=='octobus' else ['python','-m','agent.v2.capability_server',service]
        run(['run','-d','--network','none','--name',name,'-e','CODEAUDIT_WORKSPACES=/tmp/codeaudit-workspaces','-e','OCTOBUS_ADDR=127.0.0.1:9000','-e','OCTOBUS_DATA_DIR=/tmp/octobus',image,*command])
        check=['octobus','status'] if service=='octobus' else ['python','-c',"import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/health',timeout=3).read().decode())"]
        last=None
        for attempt in range(10):
            time.sleep(1)
            try:run(['exec',name,*check]);last=None;break
            except RuntimeError as e:last=e
        if last:raise last
        time.sleep(2)
        assert run(['inspect','--format','{{.State.Running}}',name])=='true'
    print('DOCKER_SMOKE=PASS',flush=True)
finally:
    for name in created:
        logs=subprocess.run(['docker','logs',name],capture_output=True,text=True,timeout=30)
        print(json.dumps({'container':name,'logs_stdout':logs.stdout,'logs_stderr':logs.stderr}),flush=True)
        subprocess.run(['docker','rm','-f',name],timeout=30,check=False)
