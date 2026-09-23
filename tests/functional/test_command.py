import copy
import shutil
from pathlib import Path
import pytest
from test_pipeline import repo, git, ROOT
from agent.analysis import analyze_candidate
from agent.preflight import inventory
from agent.report import finalize_finding, validate_finding
from agent.validator.gate import evidence_gate
from agent.evidence.model import evidence_hash
from agent.scanner.semgrep import scan
from agent.service import dispatch
from agent.config import Config

FILE = 'src/main/java/lab/CommandController.java'

@pytest.fixture
def command_repo(repo):
    shutil.copyfile(ROOT / 'fixtures/command-examples/CommandController.java', repo / FILE)
    git(repo, 'add', '.')
    git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'command')
    return repo


def finding(repo, line):
    value = finalize_finding(analyze_candidate(repo, {'file': FILE, 'line': line}), inventory(repo), 'command-test')
    validate_finding(value, ROOT / 'schemas/finding.schema.json')
    return value

@pytest.mark.parametrize('line,status', [(12, 'VERIFIED'), (17, 'NEEDS_REVIEW'), (22, 'REJECTED')])
def test_command_verdicts(command_repo, line, status):
    result = finding(command_repo, line)
    assert result['status'] == status
    assert result['category'] == 'COMMAND_INJECTION'
    if status == 'VERIFIED':
        assert all(result[x] for x in ('source', 'dataflow', 'sink', 'protection', 'reachability', 'evidence_integrity'))
        assert result['evidence_integrity']['status'] == 'PASS'

@pytest.mark.parametrize('old,new', [
    ('"printf %s " + host', '"fixed"'),
    ('"printf %s " + host', 'filter(host)'),
    ('"printf %s " + host', 'other'),
    ('String cmd = "printf %s " + host;', 'host = "fixed"; String cmd = "printf %s " + host;'),
    ('"/bin/sh", "-c", cmd', 'host, "-c", cmd'),
    ('import org.springframework.web.bind.annotation.RequestParam;', 'import fake.RequestParam;'),
])
def test_unsupported_paths_fail_closed(command_repo, old, new):
    path = command_repo / FILE
    path.write_text(path.read_text().replace(old, new))
    assert analyze_candidate(command_repo, {'file': FILE, 'line': 12})['kind'] == 'UNKNOWN'

@pytest.mark.parametrize('old,new', [
    ('Map.of(', 'Map.copyOf('),
    ('private static final', 'private static'),
    ('"127.0.0.1"', '"-f"'),
    ('HOST_MAP.get(input)', 'filter(input)'),
    ('"/usr/bin/ping", "-c", "1", mapped', 'input, "-c", "1", mapped'),
])
def test_mapping_requires_proof(command_repo, old, new):
    path = command_repo / FILE
    path.write_text(path.read_text().replace(old, new))
    assert analyze_candidate(command_repo, {'file': FILE, 'line': 22})['kind'] == 'UNKNOWN'


def test_category_and_evidence_tampering(command_repo):
    original = finding(command_repo, 12)
    for key,value in [('category', 'SQL_INJECTION'), ('dataflow', []), ('source', None)]:
        bad = copy.deepcopy(original)
        bad[key] = value
        bad['evidence_integrity']['evidence_sha256'] = evidence_hash(bad)
        assert evidence_gate(bad, command_repo)[0] == 'NEEDS_REVIEW'
    path = command_repo / FILE
    path.write_text(path.read_text().replace('"printf %s " + host', '"fixed"'))
    assert evidence_gate(original, command_repo)[0] == 'NEEDS_REVIEW'


def test_command_knowledge_disabled(command_repo):
    assert analyze_candidate(command_repo, {'file': FILE, 'line': 12}, ['KB-JAVA-COMMAND-ARGV'])['kind'] == 'UNKNOWN'


def test_real_scanner_and_service(command_repo, tmp_path):
    candidates = scan(command_repo, ROOT / 'rules/semgrep', tmp_path / 'scan')
    commands = [c for c in candidates if c['category'] == 'COMMAND_INJECTION']
    assert {c['line'] for c in commands} == {12, 17, 22}
    config = Config(command_repo.parent, tmp_path / 'results')
    for candidate in commands:
        result = dispatch('RunValidation', {'repository': command_repo.name, 'commit': git(command_repo, 'rev-parse', 'HEAD'), 'file': candidate['file'], 'line': candidate['line']}, config)
        assert result['result']['status'] == {12:'VERIFIED',17:'NEEDS_REVIEW',22:'REJECTED'}[candidate['line']]


def test_processbuilder_explicit_shell(command_repo):
    path = command_repo / FILE
    path.write_text(path.read_text().replace('Runtime.getRuntime().exec(new String[]{"/bin/sh", "-c", cmd})', 'new ProcessBuilder("/bin/sh", "-c", cmd).start()'))
    assert analyze_candidate(command_repo, {'file': FILE, 'line': 12})['kind'] == 'UNSAFE'


def test_nested_type_shadow_fails_closed(command_repo):
    path = command_repo / FILE
    path.write_text(path.read_text().replace('public class CommandController {', 'public class CommandController { class Runtime {}'))
    assert analyze_candidate(command_repo, {'file': FILE, 'line': 12})['kind'] == 'UNKNOWN'


def test_unproven_profile_fails_closed(command_repo):
    path = command_repo / FILE
    path.write_text(path.read_text().replace('@RestController', '@RestController @Profile("test")'))
    assert analyze_candidate(command_repo, {'file': FILE, 'line': 12})['kind'] == 'UNKNOWN'


def test_test_path_rejected(command_repo):
    target = command_repo / 'src/test/java/lab/CommandController.java'
    target.parent.mkdir(parents=True)
    (command_repo / FILE).rename(target)
    result = analyze_candidate(command_repo, {'file': str(target.relative_to(command_repo)), 'line':12})
    assert result['reachability'] == 'TEST_ONLY'
