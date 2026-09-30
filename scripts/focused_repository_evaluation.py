"""Round 4 diagnostics; explicitly distinguishes broad and target-guided scope."""
import json
import os
from pathlib import Path
from agent.v2.engine import Engine
from agent.v2.model import Model
from agent.v2.repository import snapshot, profile
from agent.v2.transport import OctoBus

FOCUS='Review file-serving path construction and containment across src/werkzeug/security.py and src/werkzeug/utils.py, including platform-dependent checks. Inspect the implementation and defenses; do not assume a vulnerability exists.'

def main():
    output=Path('/evaluation/round4-results.json')
    records=json.loads(output.read_text()) if output.exists() else []
    for version in ['3.0.5','3.0.6']:
        for arm in ['broad','focused']:
            key=[version,arm]
            if any(r['key']==key for r in records): continue
            audit,meta=snapshot('/evaluation/werkzeug-'+version,Path(os.environ['CODEAUDIT_WORKSPACES']))
            transport=OctoBus(os.environ['CODEAUDIT_MCP_URL'],os.environ['CODEAUDIT_OCTOBUS_TOKEN'],audit.name)
            summary=Engine(Model(),transport,audit,meta,profile(audit/'repo'),focus=FOCUS if arm=='focused' else None).run()
            records.append({'key':key,'summary':summary,'findings':json.loads((audit/'findings.json').read_text())})
            output.write_text(json.dumps(records,indent=2))
            print(json.dumps({'key':key,'status':summary['status'],'audit_id':audit.name}),flush=True)

if __name__=='__main__':main()
