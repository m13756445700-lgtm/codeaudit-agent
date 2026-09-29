"""Final verdict recomputed from committed code, never from LLM assertions."""
from agent.evidence.model import verify_references, evidence_hash
from agent.analysis import analyze_candidate


def evidence_gate(finding, repository=None, disabled_rules=()):
    if repository is None or not verify_references(repository, finding):
        return 'NEEDS_REVIEW', 'STALE_OR_INVALID_EVIDENCE'
    integrity = finding.get('evidence_integrity') or {}
    if integrity.get('status') != 'PASS' or integrity.get('commit') != finding.get('repository', {}).get('commit') or integrity.get('evidence_sha256') != evidence_hash(finding):
        return 'NEEDS_REVIEW', 'INVALID_EVIDENCE_MANIFEST'
    sink = finding.get('sink') or {}
    try:
        actual = analyze_candidate(repository, {'file': sink['file'], 'line': sink['line']}, disabled_rules=disabled_rules)
    except (OSError, ValueError, KeyError):
        return 'NEEDS_REVIEW', 'ANALYSIS_UNAVAILABLE'
    if finding.get('category') != actual.get('category', 'SQL_INJECTION'):
        return 'NEEDS_REVIEW', 'CATEGORY_MISMATCH'
    if actual['kind'] == 'UNKNOWN':
        return 'NEEDS_REVIEW', 'INCOMPLETE_DATAFLOW_OR_UNKNOWN_PROTECTION'
    for key in ('source', 'sink', 'dataflow', 'protection', 'reachability', 'rules_applied', 'knowledge_version'):
        if finding.get(key) != actual.get(key):
            return 'NEEDS_REVIEW', 'EVIDENCE_DOES_NOT_MATCH_INDEPENDENT_ANALYSIS'
    if actual['reachability'] in ('TEST_ONLY', 'DEAD_CODE'):
        return 'REJECTED', 'NON_PRODUCTION_PATH'
    if actual['reachability'] != 'PRODUCTION_REACHABLE':
        return 'NEEDS_REVIEW', 'UNKNOWN_REACHABILITY'
    if actual['protection']['status'] == 'VALID':
        return 'REJECTED', 'EFFECTIVE_PROTECTION'
    if actual['protection']['status'] not in ('ABSENT', 'INEFFECTIVE'):
        return 'NEEDS_REVIEW', 'UNKNOWN_PROTECTION'
    if not actual['protection']['evidence'] or len(actual['dataflow']) < 4:
        return 'NEEDS_REVIEW', 'INCOMPLETE_EVIDENCE'
    return 'VERIFIED', 'INDEPENDENT_SOURCE_TO_SINK_PROOF'
