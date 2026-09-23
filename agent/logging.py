import json
from datetime import datetime, timezone

FIELDS = ("run_id", "method", "candidate_id", "rule_id", "finding_id", "status")

def event(path, **values):
    # Only structured identifiers; no prompts, source, secrets or raw stderr.
    record = {key: str(values.get(key, ""))[:256] for key in FIELDS}
    record["timestamp"] = datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as output:
        output.write(json.dumps(record, ensure_ascii=False) + "\n")
