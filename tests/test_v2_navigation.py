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
