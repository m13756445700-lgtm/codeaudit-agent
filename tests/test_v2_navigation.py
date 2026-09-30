from agent.v2.repository import snapshot
from agent.v2.tools import ToolLayer


def test_ast_navigation_distinguishes_definition_call_and_comment(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'helpers.py').write_text('def execute(value):\n    return value\n')
    (src/'app.py').write_text('from helpers import execute as launch\n# execute is not a call\ndef route(value):\n    return launch(value)\n')
    audit, _ = snapshot(src, tmp_path/'ws')
    tools = ToolLayer(audit)
    result = tools.call('repo.find_callers', {'query': 'execute'})
    assert len(result['matches']) == 1
    assert result['matches'][0]['callee'] == 'helpers.execute'
    assert result['matches'][0]['caller'] == 'app.route'
    assert result['matches'][0]['line'] == 4
    definitions = tools.call('repo.find_symbol', {'query': 'execute'})
    assert definitions['matches'][0]['file'] == 'helpers.py'
    callees = tools.call('repo.find_callees', {'query': 'route'})
    assert callees['matches'] == result['matches']


def test_dynamic_call_is_explicitly_unresolved(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'app.py').write_text('def route(obj):\n    return obj.execute()\n')
    audit, _ = snapshot(src, tmp_path/'ws')
    result = ToolLayer(audit).call('repo.find_callees', {'query': 'route'})
    assert result['matches'][0]['callee'] is None
    assert result['matches'][0]['resolution'] == 'unresolved'


def test_tree_limits_navigation_to_requested_directory(tmp_path):
    src = tmp_path/'src'; src.mkdir()
    (src/'pkg').mkdir()
    (src/'pkg/a.py').write_text('x=1\n')
    (src/'README.md').write_text('unrelated\n')
    audit, _ = snapshot(src, tmp_path/'ws')
    result = ToolLayer(audit).call('repo.tree', {'path': 'pkg'})
    assert result['files'] == ['pkg/a.py']
    assert result['total'] == 1


def test_src_layout_absolute_and_relative_imports(tmp_path):
    src = tmp_path/'source'; (src/'src/pkg').mkdir(parents=True)
    (src/'src/pkg/__init__.py').write_text('')
    (src/'src/pkg/store.py').write_text('def fetch(value):\n    return value\n')
    (src/'src/pkg/routes.py').write_text('from pkg.store import fetch\nfrom .store import fetch as other\ndef route(v):\n    return fetch(v), other(v)\n')
    audit, _ = snapshot(src, tmp_path/'ws')
    result = ToolLayer(audit).call('repo.find_callers', {'query':'pkg.store.fetch'})
    assert len(result['matches']) == 2
    assert all(c['callee'] == 'pkg.store.fetch' for c in result['matches'])


def test_duplicate_symbol_is_ambiguous(tmp_path):
    src = tmp_path/'source'; src.mkdir()
    (src/'app.py').write_text('def run(x):\n    return x\ndef run(x):\n    return x + 1\ndef caller(x):\n    return run(x)\n')
    audit, _ = snapshot(src, tmp_path/'ws')
    result = ToolLayer(audit).call('repo.find_callees', {'query':'caller'})
    assert result['matches'][0]['callee'] is None
    assert result['matches'][0]['resolution'] == 'ambiguous'
