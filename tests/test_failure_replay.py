"""Offline replay of a preserved wrong rejection; no model call or relabeling."""
import copy
import hashlib
import json
from pathlib import Path
from agent.v2.gate import validate
from agent.v2.repository import snapshot
from agent.v2.tools import ToolLayer

FIXTURE = Path(__file__).parent/'fixtures/acceptance-replay'


def test_job91_original_import_based_rejection_is_blocked(tmp_path):
    record = json.loads((FIXTURE/'job91.json').read_text())
    source = (FIXTURE/'shared_data.py.txt').read_bytes()
    assert hashlib.sha256(source).hexdigest() == record['source_sha256']
    path = tmp_path/'input'/record['source_path']
    path.parent.mkdir(parents=True)
    path.write_bytes(source)
    audit, metadata = snapshot(tmp_path/'input', tmp_path/'ws')
    receipts = [ToolLayer(audit).read(record['source_path'], 1, 120)]
    original = record['finding']
    assert original['status'] == 'REJECTED' and original['evidence_gate']['passed']
    # Empty new fields isolate the import-proof check from schema-version rejection.
    candidate = copy.deepcopy(original)
    candidate.update(defense_claims=[], environment_assumptions=[])
    checked = validate(candidate, audit/'repo', metadata, receipts,
                       {key:'replay-only' for key in candidate['knowledge_used']})
    assert checked['status'] == 'INSUFFICIENT_EVIDENCE'
    assert checked['evidence_gate']['problems'] == [
        'reference:counter_evidence[0]:dependency import is not implementation evidence']
    assert original['status'] == 'REJECTED' and original['evidence_gate']['passed']
