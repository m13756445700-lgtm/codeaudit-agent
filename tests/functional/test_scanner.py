import sys
from pathlib import Path
import pytest
from agent.scanner.semgrep import scan, ScanError
ROOT = Path(__file__).resolve().parents[2]

def test_real_semgrep_sql_candidates(tmp_path):
    candidates = scan(ROOT / "fixtures/spring-security-lab", ROOT / "rules/semgrep", tmp_path, executable=str(Path(sys.executable).parent / "semgrep"))
    assert {c["rule_id"] for c in candidates} == {"mybatis-raw-substitution", "mybatis-parameter-binding"}
    assert len(candidates) == 2
    assert all("status" not in c for c in candidates)

def test_scanner_failure_never_clean(tmp_path):
    with pytest.raises(ScanError, match="SCAN_FAILED"):
        scan(ROOT / "fixtures/spring-security-lab", ROOT / "rules/semgrep", tmp_path, executable="/nonexistent/semgrep")
    assert len(list(tmp_path.glob("*.stderr"))) == 2
    assert not (tmp_path / "candidates.json").exists()
