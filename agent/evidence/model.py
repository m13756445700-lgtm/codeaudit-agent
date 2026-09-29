"""Evidence references are content-addressed and repository-relative."""

import hashlib
import json
from pathlib import Path


def reference(repository, file, line, end_line=None, symbol="", type=""):
    repository = Path(repository).resolve()
    relative = Path(file)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Evidence path must be repository-relative")
    path = (repository / relative).resolve()
    if not path.is_relative_to(repository) or not path.is_file():
        raise ValueError("Evidence file is outside repository")
    lines = path.read_text(encoding="utf-8", errors="strict").splitlines()
    end_line = end_line or line
    if line < 1 or end_line < line or end_line > len(lines):
        raise ValueError("Evidence line range is invalid")
    snippet = "\n".join(lines[line - 1:end_line]).encode("utf-8")
    return {
        "file": relative.as_posix(),
        "line": line,
        "end_line": end_line,
        "snippet_hash": hashlib.sha256(snippet).hexdigest(),
        "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "symbol": symbol,
        "type": type,
    }


def evidence_hash(finding):
    keys = ("category", "source", "sink", "dataflow", "protection", "reachability", "rules_applied", "decision_trace")
    keys = keys + ("repository", "agent_version", "rule_version", "knowledge_version")
    canonical = json.dumps({key: finding.get(key) for key in keys}, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def verify_references(repository, finding):
    """Re-read committed bytes; never trust caller-provided PASS or hashes."""
    from agent.preflight import inventory
    try:
        manifest = inventory(repository, commit=finding["repository"]["commit"])
        if manifest["branch"] != finding["repository"]["branch"]:
            return False
        references = [finding.get("source"), finding["sink"]]
        references += finding.get("dataflow", [])
        references += finding.get("protection", {}).get("evidence", [])
        for ref in filter(None, references):
            current = reference(repository, ref["file"], ref["line"], ref["end_line"], ref["symbol"], ref.get("type", ""))
            if current != ref:
                return False
        return True
    except (OSError, ValueError, KeyError, TypeError, RuntimeError):
        return False
