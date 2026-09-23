import json
import subprocess
import sys
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator
from agent.config import Config
from agent.logging import event

ROOT = Path(__file__).resolve().parents[2]

def test_schema_compiles():
    schema = json.loads((ROOT / "schemas/finding.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    assert list(Draft202012Validator(schema).iter_errors({"status": "VERIFIED"}))

def test_config_boundary(tmp_path):
    config = Config(tmp_path, tmp_path / "output")
    assert config.repository(".") == tmp_path
    with pytest.raises(ValueError):
        config.repository("..")
    (tmp_path / "escape").symlink_to(tmp_path.parent)
    with pytest.raises(ValueError):
        config.repository("escape")

def test_limits(tmp_path):
    with pytest.raises(ValueError):
        Config(tmp_path, tmp_path, max_slice_lines=0)

def test_log_allowlist(tmp_path):
    path = tmp_path / "events.jsonl"
    event(path, run_id="run1", method="INIT", status="STARTED", api_key="never-log")
    record = json.loads(path.read_text())
    assert record["run_id"] == "run1"
    assert "never-log" not in path.read_text()
    assert set(record) == {"run_id", "timestamp", "method", "candidate_id", "rule_id", "finding_id", "status"}

def test_cli():
    result = subprocess.run([sys.executable, "-m", "agent.cli", "--version"], capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0
    assert result.stdout.strip() == "CodeAudit 1.0.0"
