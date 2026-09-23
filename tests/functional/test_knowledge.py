from test_pipeline import repo, XML, git
from agent.analyzer import analyze_sql_candidate
from agent.preflight import inventory
from agent.report import finalize_finding, validate_finding
from agent.knowledge.loader import load
from test_pipeline import ROOT


def test_allowlist_switch_runtime_proof(repo):
    p = repo / 'src/main/java/lab/UserService.java'
    p.write_text(p.read_text().replace('return mapper.raw(order);', '''String field;
  switch(order) {
   case "name": field = "username"; break;
   case "time": field = "id"; break;
   default: field = "id"; break;
  }
  return mapper.raw(field);'''))
    git(repo, 'add', '.')
    git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'mapping')
    enabled = analyze_sql_candidate(repo, {'file': XML, 'line': 5})
    finding = finalize_finding(enabled, inventory(repo), 'raw')
    assert finding['status'] == 'REJECTED'
    assert 'KB-MYBATIS-SQL-FP-ALLOWLIST' in finding['rules_applied']
    validate_finding(finding, ROOT / 'schemas/finding.schema.json')
    disabled = ('KB-MYBATIS-SQL-FP-ALLOWLIST',)
    unknown = analyze_sql_candidate(repo, {'file': XML, 'line': 5}, disabled)
    other = finalize_finding(unknown, inventory(repo), 'raw', knowledge_version=load(disabled)[1], disabled_rules=disabled)
    assert other['status'] == 'NEEDS_REVIEW'
    assert finding['knowledge_version'] != other['knowledge_version']
    assert finding['decision_trace'] != other['decision_trace']
