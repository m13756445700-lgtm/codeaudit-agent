"""Predeclared live evaluation. Inputs are operator-prepared pinned local archives."""
import json
from pathlib import Path
import os
from agent.v2.repository import snapshot, profile
from agent.v2.engine import Engine
from agent.v2.model import Model
from agent.v2.transport import OctoBus


def main():
    output = Path('/evaluation/results.json')
    results = json.loads(output.read_text()) if output.exists() else []
    for version in ['3.0.5', '3.0.6']:
        for knowledge in [True, False]:
            for repeat in range(2):
                key = [version, knowledge, repeat]
                if any(r['key'] == key for r in results):
                    continue
                audit, metadata = snapshot('/evaluation/werkzeug-'+version, Path(os.environ['CODEAUDIT_WORKSPACES']))
                transport = OctoBus(os.environ['CODEAUDIT_MCP_URL'], os.environ['CODEAUDIT_OCTOBUS_TOKEN'], audit.name)
                result = Engine(Model(), transport, audit, metadata, profile(audit/'repo'), knowledge=knowledge).run()
                results.append({'key': key, 'summary': result, 'findings': json.loads((audit/'findings.json').read_text()),
                                'judgment': 'PENDING independent post-run human review against frozen target'})
                output.write_text(json.dumps(results, indent=2))
                print(json.dumps({'key': key, 'audit_id': audit.name, 'status': result['status']}), flush=True)

if __name__ == '__main__':
    main()
