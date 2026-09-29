import shutil
import subprocess
from pathlib import Path
import pytest
from agent.analyzer import analyze_sql_candidate
from agent.preflight import inventory, PreflightError
from agent.evidence.model import reference, verify_references

ROOT = Path(__file__).resolve().parents[2]
XML = 'src/main/resources/mapper/UserMapper.xml'

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

@pytest.fixture
def repo(tmp_path):
    path = tmp_path / 'lab'
    shutil.copytree(ROOT / 'fixtures/spring-security-lab', path)
    git(path, 'init', '-b', 'main')
    git(path, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'add', '.')
    git(path, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'fixture')
    return path

def test_real_call_chain(repo):
    result = analyze_sql_candidate(repo, {'file': XML, 'line': 5})
    assert result['kind'] == 'UNSAFE'
    assert any(x['file'].endswith('UserService.java') for x in result['dataflow'])
    assert any(x['file'].endswith('UserMapper.java') for x in result['dataflow'])
    assert result['protection']['evidence']

def test_disconnected_same_name_never_proves(repo):
    p = repo / 'src/main/java/lab/UserService.java'
    p.write_text(p.read_text().replace('mapper.raw(order)', 'mapper.raw("id")'))
    assert analyze_sql_candidate(repo, {'file': XML, 'line': 5})['kind'] == 'UNKNOWN'

def test_unrecognized_filter_never_absent(repo):
    p = repo / 'src/main/java/lab/UserService.java'
    p.write_text(p.read_text().replace('mapper.raw(order)', 'mapper.raw(filter(order))'))
    assert analyze_sql_candidate(repo, {'file': XML, 'line': 5})['kind'] == 'UNKNOWN'

def test_binding_is_separate(repo):
    result = analyze_sql_candidate(repo, {'file': XML, 'line': 8})
    assert result['kind'] == 'SAFE_BINDING'
    assert result['protection']['status'] == 'VALID'

def test_fixed_commit_and_dirty_rejection(repo):
    manifest = inventory(repo)
    assert manifest['commit'] == git(repo, 'rev-parse', 'HEAD')
    (repo / 'untracked.java').write_text('')
    with pytest.raises(PreflightError, match='DIRTY'):
        inventory(repo)

def test_integrity_detects_mutation(repo):
    manifest = inventory(repo)
    ref = reference(repo, XML, 5)
    finding = {'repository': {'commit': manifest['commit'], 'branch': manifest['branch']}, 'sink': ref}
    assert verify_references(repo, finding)
    (repo / XML).write_text((repo / XML).read_text().replace('ORDER BY', 'WHERE'))
    assert not verify_references(repo, finding)
