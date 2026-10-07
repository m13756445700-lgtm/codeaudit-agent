from pathlib import Path

import pytest

from scripts.replay_runtime_evidence import PINNED, replay


def test_modified_upstream_source_is_never_executed(tmp_path: Path):
    marker = tmp_path / 'executed'
    version = next(iter(PINNED))
    (tmp_path / f'ntpath-{version}.py.txt').write_text(
        f"open({str(marker)!r}, 'w').write('executed')\n"
    )
    with pytest.raises(ValueError, match='Source hash mismatch'):
        replay(tmp_path)
    assert not marker.exists()


def test_modified_posix_source_is_never_executed(tmp_path: Path):
    from scripts.replay_runtime_evidence import replay_posix
    marker = tmp_path / 'executed'
    (tmp_path / 'posixpath-3.11.1.py.txt').write_text(f"open({str(marker)!r}, 'w').write('executed')\n")
    with pytest.raises(ValueError, match='Source hash mismatch'):
        replay_posix(tmp_path)
    assert not marker.exists()
