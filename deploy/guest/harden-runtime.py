"""Patch only the version-pinned runner; abort if its expected shape changed."""
from pathlib import Path
import sys
methods = ["inventory_repository", "scan_candidates", "read_code_slice", "hash_evidence", "run_validation"]
# Pin approvals to the five controlled local service tools; no server-wide approval.
import json
prefix = sys.argv[2] if len(sys.argv) > 2 else "code-audit-service__code-audit-local__"
import re
if not re.fullmatch(r"[a-z0-9_-]+__[a-z0-9_-]+__", prefix):
    raise SystemExit("Invalid controlled tool prefix")
approved_tools = [prefix + m for m in methods]
overrides = {"mcp_servers.octobus.enabled_tools": approved_tools}
for tool in approved_tools:
    overrides["mcp_servers.octobus.tools." + tool + ".approval_mode"] = "approve"
extra = ", " + ", ".join(json.dumps(k) + ": " + json.dumps(v) for k, v in overrides.items())
p = Path(sys.argv[1])
s = p.read_text()
changes = {
 'sandboxMode: "danger-full-access"': 'sandboxMode: "read-only"',
 'networkAccessEnabled: true': 'networkAccessEnabled: false',
 'config: { developer_instructions: this.options.systemContext }': 'config: { developer_instructions: this.options.systemContext, "features.shell_tool": false, "features.unified_exec": false, "features.apply_patch_freeform": false, web_search: "disabled"' + extra + ' }',
}
for old, new in changes.items():
    if s.count(old) != 1:
        raise SystemExit('Unsupported runner shape; refusing partial hardening: ' + old)
    s = s.replace(old, new)
p.write_text(s)
