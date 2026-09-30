"""Execute only project-authored fixtures to validate their declared counterexamples.
The audit engine never imports or executes repositories under audit.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT = Path(__file__).resolve().parents[1]/'evaluation'
CASES = json.loads((ROOT/'business-ground-truth.json').read_text())['cases']


@pytest.mark.parametrize('case', CASES, ids=lambda c:c['id'])
def test_business_pair_ground_truth(case):
    source = ROOT/case['source']
    assert {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts} == case['files_sha256']
    package = 'fixture_' + case['id'].replace('-', '_')
    spec = importlib.util.spec_from_file_location(package, source/'src/billing/__init__.py', submodule_search_locations=[str(source/'src/billing')])
    module = importlib.util.module_from_spec(spec); sys.modules[package] = module
    spec.loader.exec_module(module)
    service = importlib.import_module(package+'.service')
    a = SimpleNamespace(tenant_id='A', role='editor')
    b = SimpleNamespace(tenant_id='B', role='editor')
    db = {'a': {'tenant_id':'A', 'memo':'private-A'}, 'b': {'tenant_id':'B', 'memo':'private-B'}}
    cache = {}
    payload = {'invoice_id':'a', 'invoice_ids':['b','a'], 'memo':'changed-by-B'}
    try:
        if 'cache' in case['id']:
            service.perform(a, payload, db, cache)
        if case['target']['expected'] == 'REJECTED':
            with pytest.raises(PermissionError): service.perform(b, payload, db, cache)
            assert db['a']['memo'] == 'private-A'
        else:
            result = service.perform(b, payload, db, cache)
            assert any(r['tenant_id'] == 'A' for r in (result if isinstance(result, list) else [result]))
            if 'update' in case['id']:
                assert db['a']['memo'] == 'changed-by-B'
    finally:
        for name in list(sys.modules):
            if name == package or name.startswith(package+'.'):
                del sys.modules[name]
