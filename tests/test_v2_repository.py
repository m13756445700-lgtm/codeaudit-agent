import zipfile
import pytest
from agent.v2.repository import snapshot, profile, Limits, safe_path


def test_local_snapshot_and_profile(tmp_path):
    source = tmp_path / 'source'
    source.mkdir()
    (source / 'app.py').write_text('from fastapi import FastAPI\n@app.get("/search")\ndef search(q): return service.find(q)\n')
    audit, metadata = snapshot(source, tmp_path / 'workspaces')
    (source / 'app.py').write_text('changed')
    assert 'fastapi' in (audit / 'repo/app.py').read_text()
    assert metadata['file_count'] == 1
    result = profile(audit / 'repo')
    assert result['languages'] == {'Python': 1}
    assert result['frameworks'] == ['FastAPI']
    assert result['audit_priorities'] is None


def test_unknown_language_not_rejected(tmp_path):
    source = tmp_path / 'src'
    source.mkdir()
    (source / 'app.ex').write_text('defmodule Web do\nend')
    audit, _ = snapshot(source, tmp_path / 'ws')
    assert profile(audit / 'repo')['mode'] == 'generic'


@pytest.mark.parametrize('name', ['../escape', '/absolute', 'x/../../escape', 'x\\escape'])
def test_zip_slip_and_cleanup(tmp_path, name):
    archive = tmp_path / 'src.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr(name, 'bad')
    with pytest.raises(ValueError):
        snapshot(archive, tmp_path / 'ws')
    assert list((tmp_path / 'ws').iterdir()) == []


def test_zip_and_limits(tmp_path):
    archive = tmp_path / 'src.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('src/a.go', 'package main')
    audit, _ = snapshot(archive, tmp_path / 'ws')
    assert profile(audit / 'repo')['languages'] == {'Go': 1}
    with pytest.raises(ValueError):
        snapshot(archive, tmp_path / 'ws', Limits(max_file=2))


def test_symlink_and_embedded_credentials(tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    (src / 'link').symlink_to('/etc/passwd')
    with pytest.raises(ValueError):
        snapshot(src, tmp_path / 'ws')
    with pytest.raises(ValueError):
        snapshot('https://user:password@example.org/repo.git', tmp_path / 'ws')


def test_safe_path_rejects_existing_symlink(tmp_path):
    (tmp_path / 'link').symlink_to('/tmp')
    with pytest.raises(ValueError):
        safe_path(tmp_path, 'link/file')


def test_revision_diff_uses_parent_and_bounds_output(tmp_path):
    import subprocess
    from agent.v2.repository import revision_diff
    def git(*args):
        return subprocess.check_output(['git', '-C', str(tmp_path), *args], stderr=subprocess.DEVNULL)
    git('init')
    (tmp_path / 'app.py').write_text('value = 1\n')
    git('add', '.')
    git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'initial')
    initial = revision_diff(tmp_path)
    assert initial['comparison'] == 'initial-commit' and '+value = 1' in initial['patch']
    (tmp_path / 'app.py').write_text('value = 2\n' + '# added line\n' * 2000)
    git('add', '.')
    git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-m', 'change')
    changed = revision_diff(tmp_path)
    assert changed['base_commit'] == initial['commit']
    assert changed['truncated'] is True
    assert '-value = 1' in changed['patch'] and '+value = 2' in changed['patch']
    assert len(changed['patch'].encode()) <= 12000
