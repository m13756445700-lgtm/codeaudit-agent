"""Explicit experimental knowledge arms; original MCP result hash retained for provenance."""
import hashlib
import json
import os
from pathlib import Path
from agent.v2.repository import snapshot, profile
from agent.v2.engine import Engine
from agent.v2.model import Model
from agent.v2.transport import OctoBus

GENERIC = 'Assess untrusted input, reachability, security impact, authorization and sanitization. Confirm only evidence-supported vulnerabilities. Reject effective defenses. State unknowns and limitations. Do not execute target code.'

class GenericKnowledge:
    kind = 'octobus-mcp+explicit-generic-knowledge-ablation'
    def __init__(self, transport): self.transport = transport
    def call(self, name, arguments):
        result = self.transport.call(name, arguments)
        if name != 'knowledge.retrieve': return result
        return {'id': 'generic-ablation.md', 'sha256': hashlib.sha256(GENERIC.encode()).hexdigest(),
                'content': GENERIC, 'ablation_transform': 'Original category knowledge replaced with generic text by evaluation harness only',
                'original_document': result.get('id'), 'original_sha256': result.get('sha256')}


def main():
    output=Path('/evaluation/knowledge-results.json')
    records=json.loads(output.read_text()) if output.exists() else []
    for case in ['java-runtime-string','false-positive','cross-file-flow']:
        for repeat in range(2):
            for arm in ['on','off','generic']:
                key=[case,repeat,arm]
                if any(r['key']==key for r in records): continue
                audit,meta=snapshot('/opt/codeaudit/benchmark/'+case,Path(os.environ['CODEAUDIT_WORKSPACES']))
                transport=OctoBus(os.environ['CODEAUDIT_MCP_URL'],os.environ['CODEAUDIT_OCTOBUS_TOKEN'],audit.name)
                if arm=='generic': transport=GenericKnowledge(transport)
                result=Engine(Model(),transport,audit,meta,profile(audit/'repo'),knowledge=arm!='off').run()
                findings=json.loads((audit/'findings.json').read_text())
                records.append({'key':key,'summary':result,'findings':findings})
                output.write_text(json.dumps(records,indent=2))
                print(json.dumps({'key':key,'status':result['status'],'findings':[f['status'] for f in findings]}),flush=True)

if __name__=='__main__':main()
