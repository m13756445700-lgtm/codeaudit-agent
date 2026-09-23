from copy import deepcopy
from test_pipeline import repo, ROOT, XML
from agent.preflight import inventory
from agent.analyzer import analyze_sql_candidate
from agent.report import finalize_finding, validate_finding, write_report
from agent.validator.gate import evidence_gate
from agent.evidence.model import evidence_hash


def result(repo, line=5):
    return finalize_finding(analyze_sql_candidate(repo, {'file': XML, 'line': line}), inventory(repo), 'mybatis-raw-substitution')

def test_sqli_end_to_end_gate(repo, tmp_path):
    finding = result(repo)
    assert finding['status'] == 'VERIFIED'
    validate_finding(finding, ROOT / 'schemas/finding.schema.json')
    assert evidence_gate(finding, repo)[0] == 'VERIFIED'
    assert finding['evidence_integrity']['evidence_sha256'] == evidence_hash(finding)
    write_report([finding], tmp_path, ROOT / 'schemas/finding.schema.json')
    assert (tmp_path / 'report.md').exists()

def test_bound_finding_schema(repo):
    finding = result(repo, 8)
    assert finding['status'] == 'REJECTED'
    validate_finding(finding, ROOT / 'schemas/finding.schema.json')

def test_forged_flow_rejected(repo):
    finding = result(repo)
    finding['dataflow'] = [finding['source'], finding['sink']]
    finding['evidence_integrity']['evidence_sha256'] = evidence_hash(finding)
    assert evidence_gate(finding, repo)[0] == 'NEEDS_REVIEW'

def test_each_evidence_category_required(repo):
    finding = result(repo)
    for key in ('source', 'sink', 'dataflow', 'protection', 'reachability', 'evidence_integrity'):
        tampered = deepcopy(finding)
        tampered.pop(key)
        assert evidence_gate(tampered, repo)[0] != 'VERIFIED'

def test_stale_after_commit_change(repo):
    finding = result(repo)
    (repo / XML).write_text('changed')
    assert evidence_gate(finding, repo)[0] == 'NEEDS_REVIEW'
