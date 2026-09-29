"""Real local SSH authentication test; disposable keys never enter the repository."""
import atexit,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent.v2.repository import snapshot
root=Path(tempfile.mkdtemp(prefix='codeaudit-ssh-test-'))
atexit.register(shutil.rmtree,root,True)
src=root/'source';src.mkdir()
(src/'app.py').write_text('value = 1\n')
def run(*args):return subprocess.check_output(list(args),stderr=subprocess.DEVNULL,text=True,timeout=90).strip()
run('git','init',str(src));run('git','-C',str(src),'add','.');run('git','-C',str(src),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','fixture')
run('git','clone','--bare',str(src),str(root/'repo.git'))
run('ssh-keygen','-q','-t','ed25519','-N','','-f',str(root/'id'))
container=run('docker','run','-d','--rm','-p','127.0.0.1::2222','-v',str(root)+':/fixture:ro','codeaudit-ssh-fixture:local')
try:
 port=run('docker','port',container,'2222/tcp').rsplit(':',1)[1]
 key=run('docker','exec',container,'cat','/etc/ssh/ssh_host_ed25519_key.pub')
 (root/'known_hosts').write_text(f'[127.0.0.1]:{port} '+key+'\n')
 os.environ['GIT_SSH_COMMAND']=f'ssh -i {root}/id -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile={root}/known_hosts'
 directory,meta=snapshot(f'ssh://root@127.0.0.1:{port}/fixture/repo.git',root/'workspaces')
 assert (directory/'repo/app.py').read_text()=='value = 1\n'
 assert meta['commit']==run('git','-C',str(src),'rev-parse','HEAD')
 assert 'PRIVATE KEY' not in json.dumps(meta)
 print(json.dumps({'passed':True,'protocol':'ssh','authenticated':True,'host_key_check':'strict, pinned from controlled container','files':meta['file_count'],'revision_diff':bool(meta.get('revision_diff_sha256')),'scope':'local real SSH Git fixture, no third-party account access claimed'}))
finally:
 run('docker','stop',container)
