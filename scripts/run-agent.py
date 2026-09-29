"""Launch the existing Engine without agent-compose's provider proxy overrides."""
import os
from agent.v2.cli import main

if __name__ == '__main__':
    for suffix in ('API_ENDPOINT', 'API_KEY', 'MODEL'):
        value = os.environ.get('CODEAUDIT_LLM_' + suffix)
        if not value:
            raise SystemExit('Missing dedicated audit model setting: ' + suffix)
        os.environ['LLM_' + suffix] = value
    raise SystemExit(main())
