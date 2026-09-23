import argparse
import json
from pathlib import Path
from agent.config import Config
from agent.preflight import inventory
from agent.scanner.semgrep import scan
from agent.analysis import analyze_candidate
from agent.report import finalize_finding, write_report

def main():
    parser = argparse.ArgumentParser(description="Evidence-based Java security audit")
    parser.add_argument("--version", action="version", version="CodeAudit 1.0.0")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check-config")
    check.add_argument("--repository-root", type=Path, required=True)
    check.add_argument("--output-root", type=Path, required=True)
    audit = commands.add_parser("audit")
    audit.add_argument("--repository", type=Path, required=True)
    audit.add_argument("--rules", type=Path, required=True)
    audit.add_argument("--output", type=Path, required=True)
    audit.add_argument("--branch")
    audit.add_argument("--commit")
    args = parser.parse_args()
    if args.command == "check-config":
        config = Config(args.repository_root, args.output_root)
        config.repository(".")
        print(json.dumps({"status": "VALID", "agent_version": "1.0.0"}))
        return
    if args.command == "audit":
        manifest = inventory(args.repository, branch=args.branch, commit=args.commit)
        artifacts = args.output / "artifacts"
        candidates = scan(args.repository, args.rules, artifacts)
        findings = []
        for candidate in candidates:
            analyzed = analyze_candidate(args.repository, candidate)
            findings.append(finalize_finding(analyzed, manifest, candidate["rule_id"]))
        write_report(findings, args.output, Path(__file__).resolve().parents[1] / "schemas/finding.schema.json")
        print(json.dumps({"status": "DONE", "manifest": manifest, "findings": len(findings)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
