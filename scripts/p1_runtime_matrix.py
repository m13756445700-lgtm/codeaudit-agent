"""Run with an isolated --target install on PYTHONPATH. Finite observed versions only."""
import json,sys,os,ntpath,posixpath
from importlib.metadata import version
from werkzeug.security import safe_join
from urllib3.util import parse_url
rows=[]
for value in ('../outside','inside/report','/absolute',r'folder\..\report',r'\\host\share\report'):
 result=safe_join('base',value)
 rows.append({'input':value,'safe_join':result,'ntpath_isabs':ntpath.isabs(value),'posixpath_isabs':posixpath.isabs(value)})
assert rows[0]['safe_join'] is None and rows[1]['safe_join']=='base/inside/report' and rows[2]['safe_join'] is None
urls=[]
for raw in ('https://user@internal.invalid/a','https://allowed.invalid@internal.invalid/a','https://allowed.invalid.evil.invalid/a'):
 u=parse_url(raw);urls.append({'input':raw,'host':u.host,'auth':u.auth})
assert urls[1]['host']=='internal.invalid' and urls[2]['host']=='allowed.invalid.evil.invalid'
print(json.dumps({'python':sys.version,'os_name':os.name,'werkzeug':version('Werkzeug'),'urllib3':version('urllib3'),'paths':rows,'urls':urls,'limits':'Exact tested versions and local OS only. ntpath calculations are not Windows-host execution. No inference about intervening versions or real exploitability.'},indent=2))
