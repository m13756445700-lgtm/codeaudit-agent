import json
import subprocess
import sys
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]

def test_schema_compiles():
    schema = json.loads((ROOT / "schemas/finding.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    assert list(Draft202012Validator(schema).iter_errors({"status": "VERIFIED"}))

def test_cli():
    result = subprocess.run([sys.executable, "-m", "agent.cli", "--version"], capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0
    assert result.stdout.strip() == "CodeAudit 2.0.0"
