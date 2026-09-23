"""Run and verify actual local Agent Compose sessions; never synthesize findings."""
import argparse, json, os, subprocess, time
from pathlib import Path
from agent.workflow.validation import verify_session, OutputError
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'runs/local-recheck/phase7'
D=os.environ.get('CODEAUDIT_DOCKER','/Applications/Docker.app/Contents/Resources/bin/docker')
DAEMON=os.environ.get('CODEAUDIT_DAEMON_CONTAINER','codeaudit-local-agent-compose')
OCTOBUS=os.environ.get('CODEAUDIT_OCTOBUS_CONTAINER','codeaudit-local-octobus')
REPO='lab'
COMMIT='af482b5a62e1af3b8fae3908328f229852986337'
CLI=[D,'exec',DAEMON,'agent-compose','--host','http://127.0.0.1:7410','-f',os.environ.get('CODEAUDIT_PROJECT_CONFIG','/data/agent-compose.yml')]
def execute(args):
    return subprocess.check_output(args,text=True,timeout=30)

def collect(run_id, destination):
    deadline=time.monotonic()+330
    while True:
        run=json.loads(execute(CLI+['inspect','run',run_id]))
        if run['status'] in {'succeeded','failed','cancelled','stopped'}: break
        if time.monotonic()>deadline: raise TimeoutError('RUN_WAIT_LIMIT')
        time.sleep(5)
    destination.mkdir(parents=True,exist_ok=True)
    (destination/'run.json').write_text(json.dumps(run,ensure_ascii=False,indent=2))
    if run['status']!='succeeded': raise OutputError('AGENT_RUN_FAILED')
    sid=run['sandbox_id']
    execute([D,'cp',f'{DAEMON}:/data/sandboxes/{sid}/home/.codex/sessions',str(destination/'sessions')])
    execute([D,'cp',f'{OCTOBUS}:/var/lib/octobus/codeaudit-runs',str(destination/'trusted-runs')])
    files=list((destination/'sessions').rglob('*.jsonl'))
    if len(files)!=1: raise OutputError('AMBIGUOUS_SESSION')
    events=[json.loads(l) for l in files[0].read_text().splitlines()]
    return run,events

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--repository', default=REPO)
    parser.add_argument('--commit', default=COMMIT)
    parser.add_argument('--output', type=Path, default=OUT)
    parser.add_argument('--max-attempts', type=int, choices=[1,2], default=2)
    options=parser.parse_args()
    REPO,COMMIT,OUT=options.repository,options.commit,options.output
    OUT.mkdir(parents=True,exist_ok=True)
    execute(CLI+['up'])
    for attempt in range(1,options.max_attempts+1):
        destination=OUT/f'attempt-{time.time_ns()}'
        prompt=f'审计 repository={REPO} commit={COMMIT}。严格按系统参数契约逐候选完成五个方法。ReadCodeSlice和HashEvidence必须逐候选使用ScanCandidates返回的file和line，只读该行，不传end_line，不合并候选，不猜测文件长度。只返回原始JSON，不使用代码围栏。每个finding完整复制RunValidation的result，禁止改写或省略。'
        text=execute(CLI+['run','auditor','--detach','--prompt',prompt])
        run_id=next(l[5:].strip() for l in text.splitlines() if l.startswith('Run: '))
        print('Attempt',attempt,'Run',run_id,flush=True)
        try:
            run,events=collect(run_id,destination)
            value=verify_session(events,destination/'trusted-runs',REPO,COMMIT)
            (destination/'verified-output.json').write_text(json.dumps(value,ensure_ascii=False,indent=2))
            result={'passed':True,'run_id':run_id,'evidence':str(destination),'statuses':[x['status'] for x in value['findings']]}
            (OUT/'result.json').write_text(json.dumps(result,indent=2))
            print(json.dumps(result),flush=True)
            break
        except OutputError as exc:
            (destination/'verification-failure.txt').write_text(str(exc))
            print('Verification rejected:',str(exc),flush=True)
    else:
        (OUT/'result.json').write_text(json.dumps({'passed':False,'reason':'RETRIES_EXHAUSTED'}))
        raise SystemExit(1)
