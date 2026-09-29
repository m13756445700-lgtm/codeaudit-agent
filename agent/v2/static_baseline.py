"""Evaluation only: preserve the existing V1 analyzer/Gate instead of zeroing verdicts.

The V2 production Engine never imports this module. Snapshot manifests are explicitly
identified as snapshots, not fabricated Git commits. V1 project preflight support is
reported separately from this more permissive analyzer comparison.
"""
from pathlib import Path
import hashlib
import json
from unittest.mock import patch
from agent.v2.repository import files, digest
from agent.analysis import analyze_candidate
from agent.report import finalize_finding


def evaluate(repo, metadata, signals):
    repo = Path(repo)
    manifest = {'repository': str(repo), 'branch': 'SNAPSHOT',
                'commit': metadata.get('commit') or 'snapshot:' + metadata['snapshot_sha256'],
                'agent_version': '1.0.0', 'rule_version': '1.0.0'}
    def snapshot_inventory(repository, **kwargs):
        # Evaluation-only adapter. Keep V1 semantic analyzer and Gate unchanged,
        # replacing only its Git/framework inventory with a verified snapshot.
        actual = {p.relative_to(repo).as_posix(): digest(p) for p in files(repo)}
        if (Path(repository).resolve() != repo.resolve() or actual != metadata['files']
                or hashlib.sha256(json.dumps(actual, sort_keys=True).encode()).hexdigest()
                != metadata['snapshot_sha256'] or kwargs.get('commit') != manifest['commit']):
            raise ValueError('Static baseline snapshot integrity mismatch')
        return manifest
    findings, errors = [], []
    for signal in signals:
        try:
            analyzed = analyze_candidate(repo, signal)
            with patch('agent.preflight.inventory', snapshot_inventory):
                findings.append(finalize_finding(analyzed, manifest, signal['rule_id']))
        except Exception as error:
            errors.append({'file': signal.get('file'), 'line': signal.get('line'),
                           'error_type': type(error).__name__})
    return {'llm_calls': 0, 'pipeline': 'unchanged V1 analyze_candidate + finalize_finding/Evidence Gate',
            'input_adapter': 'same snapshot bytes/hash; evaluation-only Git/framework inventory adapter; unchanged V1 semantic analyzer and Gate; run serially',
            'findings': findings, 'errors': errors,
            'security_verdicts': len(findings),
            'confirmed': sum(f['status'] == 'VERIFIED' for f in findings)}
