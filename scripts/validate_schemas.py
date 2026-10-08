"""Offline schema checks; no model credentials or paid API calls."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from jsonschema import Draft202012Validator
from agent.v2.engine import DECISION,TOOLS
for path in Path('schemas').glob('*.json'):
    Draft202012Validator.check_schema(json.loads(path.read_text()))
Draft202012Validator.check_schema(DECISION)
for tool in TOOLS:
    Draft202012Validator.check_schema(tool['function']['parameters'])
print('All persisted and V2 tool schemas valid')
