"""Public V2 entrypoint. Static baselines are evaluation-only."""
import sys
from agent.v2.cli import main as audit


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ['--version']:
        print('CodeAudit 2.0.0')
        return 0
    if args and args[0] == 'audit':
        args.pop(0)
    return audit(args)


if __name__ == '__main__':
    raise SystemExit(main())
