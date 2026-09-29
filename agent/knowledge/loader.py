"""Versioned data rules; runtime switches are service policy, not LLM input."""
from pathlib import Path
import hashlib
import json
import yaml

ROOT = Path(__file__).resolve().parents[2] / 'knowledge/java-spring'

def load(disabled=()):
    entries = []
    for path in sorted(ROOT.glob('*.yaml')):
        entries.extend(yaml.safe_load(path.read_text()) or [])
    ids = [r['rule_id'] for r in entries]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate knowledge rule')
    if set(disabled) - set(ids):
        raise ValueError('Unknown disabled knowledge rule')
    active = [r for r in entries if r['rule_id'] not in disabled]
    version = hashlib.sha256(json.dumps(active, sort_keys=True).encode()).hexdigest()
    return {r['rule_id']: r for r in active}, '1.0.0+' + version[:12]
