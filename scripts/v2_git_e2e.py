import os,sys,subprocess,tempfile,threading,json
from pathlib import Path
from http.server import HTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r))
root=Path(tempfile.mkdtemp(prefix='codeaudit-http-git-'));src=root/'source';src.mkdir()
for p in (r/'benchmark/cross-file-flow').glob('*.py'):(src/p.name).write_bytes(p.read_bytes())
def git(*args):return subprocess.check_output(['git',*args],stderr=subprocess.DEVNULL)
git('init',str(src));git('-C',str(src),'add','.');git('-C',str(src),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','E2E source snapshot');git('clone','--bare',str(src),str(root/'input.git'))
backend=git('--exec-path').decode().strip()+'/git-http-backend'
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):self.handle_git()
 def do_POST(self):self.handle_git()
 def handle_git(self):
  u=urlsplit(self.path);env=dict(os.environ,GIT_PROJECT_ROOT=str(root),GIT_HTTP_EXPORT_ALL='1',PATH_INFO=u.path,QUERY_STRING=u.query,REQUEST_METHOD=self.command,CONTENT_TYPE=self.headers.get('Content-Type',''),CONTENT_LENGTH=self.headers.get('Content-Length','0'))
  output=subprocess.check_output([backend],input=self.rfile.read(int(env['CONTENT_LENGTH'])),env=env)
  headers,body=output.split(b'\r\n\r\n',1);self.send_response(200)
  for line in headers.decode().split('\r\n'):
   k,v=line.split(':',1)
   if k.lower()!='status':self.send_header(k,v.strip())
  self.end_headers();self.wfile.write(body)
server=HTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
from agent.v2.cli import main
url='http://127.0.0.1:'+str(server.server_port)+'/input.git'
try:code=main([url,'--keep-source'])
finally:server.shutdown()
raise SystemExit(code)
