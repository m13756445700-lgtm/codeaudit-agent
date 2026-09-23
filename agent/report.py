"""Finding serialization and human-readable report generation."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from agent.evidence.model import evidence_hash
from agent.validator.gate import evidence_gate


def finalize_finding(candidate, manifest, rule_id, knowledge_version="1.0.0", disabled_rules=()):
    finding = {
        "finding_id": f"{candidate.get('category', 'SQL_INJECTION').lower()}-{rule_id}-{candidate['sink']['file'].replace('/', '-')}-{candidate['sink']['line']}",
        "category": candidate.get("category", "SQL_INJECTION"),
        "status": "NEEDS_REVIEW",
        "repository": {"name": Path(manifest["repository"]).name, "branch": manifest["branch"], "commit": manifest["commit"]},
        "source": candidate.get("source"),
        "sink": candidate["sink"],
        "dataflow": candidate.get("dataflow", []),
        "protection": candidate.get("protection", {"status": "UNKNOWN", "evidence": []}),
        "reachability": candidate.get("reachability", "UNKNOWN"),
        "rules_applied": candidate.get("rules_applied", [rule_id]),
        "decision_trace": [],
        "evidence_integrity": {"commit": manifest["commit"], "status": "UNCHECKED", "evidence_sha256": "0" * 64},
        "recommendation": ("Avoid shell command text; use fixed executable and immutable finite argument mapping." if candidate.get("category") == "COMMAND_INJECTION" else "Use immutable serviceId-to-URL mapping; review DNS, redirects and egress policy separately." if candidate.get("category") == "SSRF" else "Resolve real target and base paths, enforce directory boundary, and prevent concurrent filesystem mutation." if candidate.get("category") == "PATH_TRAVERSAL" else "Use parameterized binding or a finite server-side allowlist mapping."),
        "agent_version": manifest["agent_version"],
        "rule_version": manifest["rule_version"],
        "knowledge_version": candidate.get("knowledge_version", knowledge_version),
    }
    from agent.evidence.model import verify_references
    finding["evidence_integrity"]["status"] = "PASS" if verify_references(manifest["repository"], finding) else "FAIL"
    finding["evidence_integrity"]["evidence_sha256"] = evidence_hash(finding)
    finding["status"], reason = evidence_gate(finding, manifest["repository"], disabled_rules=disabled_rules)
    finding["decision_trace"].append(reason)
    finding["evidence_integrity"]["status"] = "PASS" if verify_references(manifest["repository"], finding) else "FAIL"
    finding["evidence_integrity"]["evidence_sha256"] = evidence_hash(finding)
    return finding


def validate_finding(finding, schema_path):
    schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(finding), key=lambda error: list(error.path))
    if errors:
        raise ValueError("Finding schema validation failed: " + "; ".join(error.message for error in errors))


def write_report(findings, output_dir, schema_path):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for finding in findings:
        validate_finding(finding, schema_path)
    (output_dir / "findings.json").write_text(json.dumps(findings, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# CodeAudit 审计报告", "", f"Finding 数量：{len(findings)}", ""]
    for finding in findings:
        lines.append(f"## {finding['finding_id']} — {finding['status']}")
        lines.append(f"- 类别：{finding.get('category', 'SQL_INJECTION')}")
        lines.append(f"- 结论：{finding.get('reason', finding.get('recommendation', ''))}")
        sink = finding.get("sink", {})
        lines.append(f"- 证据位置：{sink.get('file', 'n/a')}:{sink.get('line', 'n/a')}")
        lines.append("")
    (output_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
