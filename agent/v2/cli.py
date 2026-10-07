import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from agent.v2.repository import snapshot, profile
from agent.v2.tools import ToolLayer
from agent.v2.transport import Local, OctoBus
from agent.v2.model import Model
from agent.v2.engine import Engine


def main(argv=None):
    parser = argparse.ArgumentParser(description='AI-driven code audit V2')
    parser.add_argument('source', help='Git URL, ZIP, or local source directory')
    parser.add_argument('--workspaces', type=Path, default=Path(os.environ.get('CODEAUDIT_WORKSPACES', '/tmp/codeaudit-v2/workspaces')))
    parser.add_argument('--local-tools', action='store_true', help='Development adapter; not OctoBus acceptance')
    parser.add_argument('--keep-source', action='store_true', help='Retain snapshot for audit replay (otherwise cleaned after run)')
    parser.add_argument('--no-knowledge', action='store_true', help='Knowledge ablation only')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress events on stderr')
    parser.add_argument('--policy-file', type=Path, help='UTF-8 business policy supplied by the operator (at most 8000 characters); not source evidence')
    parser.add_argument('--focus', help='Optional operator-defined audit scope; not evidence or an expected verdict')
    parser.add_argument('--max-iterations', type=int, default=48)
    parser.add_argument('--max-calls', type=int, default=100)
    parser.add_argument('--timeout', type=int, default=1200, help='Audit budget in seconds; a pending model request may add up to its request timeout')
    args = parser.parse_args(argv)
    if args.focus and len(args.focus) > 1000:
        parser.error('Focus must be at most 1000 characters')
    if not 1 <= args.max_iterations <= 200 or not 1 <= args.max_calls <= 500 or not 30 <= args.timeout <= 3600:
        parser.error('Budget bounds: iterations 1..200, calls 1..500, timeout 30..3600 seconds')
    policy = None
    if args.policy_file:
        try:
            with args.policy_file.open(encoding='utf-8') as handle:
                policy = handle.read(8001)
        except (OSError, UnicodeError) as error:
            parser.error('Cannot read policy file: ' + str(error))
        if len(policy) > 8000:
            parser.error('Business policy must be at most 8000 characters')
    def progress(event):
        if not args.quiet:
            print(json.dumps(event, ensure_ascii=False), file=sys.stderr, flush=True)
    progress({'event': 'repository_intake'})
    model = Model()  # Fail before acquiring repo if credentials missing.
    audit, metadata = snapshot(args.source, args.workspaces)
    try:
        transport = Local(ToolLayer(audit)) if args.local_tools else OctoBus(
            os.environ['CODEAUDIT_MCP_URL'], os.environ['CODEAUDIT_OCTOBUS_TOKEN'], audit.name)
        repo_profile = profile(audit / 'repo')
        progress({'event': 'repository_understanding', 'languages': repo_profile['languages'], 'files': metadata['file_count']})
        result = Engine(model, transport, audit, metadata, repo_profile, knowledge=not args.no_knowledge, progress=progress, max_iterations=args.max_iterations, max_calls=args.max_calls, timeout=args.timeout, focus=args.focus, business_policy=policy, adversarial_review=True).run()
        print(json.dumps({**result, 'report': str(audit / 'report.md')}, ensure_ascii=False))
        return 0 if result['status'] == 'COMPLETE' else 2
    finally:
        if not args.keep_source:
            shutil.rmtree(audit / 'repo', ignore_errors=True)


if __name__ == '__main__':
    raise SystemExit(main())
