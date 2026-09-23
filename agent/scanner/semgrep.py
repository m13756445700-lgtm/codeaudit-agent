import json
import os
import subprocess
import sys
from pathlib import Path

class ScanError(RuntimeError):
    pass

def scan(repository, rules, artifact_dir, executable=None, timeout=60):
    """Execute fixed scanner argv; never interpret candidate data as commands."""
    repository, rules, artifact_dir = map(lambda p: Path(p).resolve(), (repository, rules, artifact_dir))
    artifact_dir.mkdir(parents=True, exist_ok=True)
    executable = executable or str(Path(sys.executable).parent / "semgrep")
    argv = [executable, "scan", "--config", str(rules), "--json", "--jobs", "1", "--metrics=off", "--disable-version-check", "--no-git-ignore", str(repository)]
    # Preserve HOME: changing it can stall native startup on this host.
    # Route only the scanner log into the controlled artifact directory.
    env = dict(os.environ, SEMGREP_LOG_FILE=str(artifact_dir / "semgrep.log"), SEMGREP_SEND_METRICS="off")
    for attempt in range(2):
        error = ""
        try:
            completed = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, env=env)
            error = completed.stderr
            if completed.returncode != 0:
                raise ScanError("Scanner exit code " + str(completed.returncode))
            payload = json.loads(completed.stdout)
            if payload.get("errors"):
                raise ScanError("Scanner reported incomplete analysis")
            if not isinstance(payload.get("results"), list):
                raise ScanError("Invalid scanner response")
            candidates = []
            for item in payload["results"]:
                path = Path(item["path"]).resolve()
                if not path.is_relative_to(repository):
                    raise ScanError("Scanner path outside repository")
                candidates.append({"rule_id": item["check_id"].split(".")[-1], "file": str(path.relative_to(repository)), "line": item["start"]["line"], "end_line": item["end"]["line"], "category": item.get("extra", {}).get("metadata", {}).get("category", "SQL_INJECTION")})
            (artifact_dir / "candidates.json").write_text(json.dumps(candidates, indent=2), encoding="utf-8")
            return sorted(candidates, key=lambda c: (c["file"], c["line"], c["rule_id"]))
        except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, ScanError) as exc:
            detail = locals().get("error", "") or (str(exc) if isinstance(exc, ScanError) else type(exc).__name__)
            log = artifact_dir / ("scanner-attempt-%d.stderr" % (attempt + 1))
            log.write_text(str(detail))
            log.chmod(0o600)
    raise ScanError("SCAN_FAILED after two attempts; findings unavailable")
