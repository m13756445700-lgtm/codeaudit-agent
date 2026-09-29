from agent.validator.gate import evidence_gate
from agent.evidence.model import evidence_hash


def test_self_asserted_pass_cannot_verify():
    ref = {"file": "nonexistent.java", "line": 1, "snippet_hash": "0" * 64}
    finding = {
        "source": ref, "sink": ref, "dataflow": [ref, ref],
        "protection": {"status": "ABSENT", "evidence": []},
        "reachability": "PRODUCTION_REACHABLE",
        "evidence_integrity": {"status": "PASS"},
    }
    finding["evidence_integrity"]["evidence_sha256"] = evidence_hash(finding)
    assert evidence_gate(finding)[0] == "NEEDS_REVIEW"


def test_nonexistent_repository_cannot_verify(tmp_path):
    assert evidence_gate({}, tmp_path)[0] == "NEEDS_REVIEW"


def test_canonical_hash_ignores_dictionary_order():
    assert evidence_hash({"source": {"file": "a", "line": 1}}) == evidence_hash({"source": {"line": 1, "file": "a"}})
