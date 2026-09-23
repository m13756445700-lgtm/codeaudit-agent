"""Deterministic repository inventory and fixed-commit preflight."""

import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path


class PreflightError(RuntimeError):
    pass


def _git(repository, *args):
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), *args],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise PreflightError("Git preflight failed") from exc
    return result.stdout.strip()


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(repository, branch=None, commit=None, agent_version="1.0.0", rule_version="1.0.0", knowledge_version="1.0.0"):
    repository = Path(repository).resolve()
    if not repository.is_dir() or not (repository / ".git").exists():
        raise PreflightError("Repository must be a Git working tree")
    if _git(repository, "status", "--porcelain", "--untracked-files=all"):
        raise PreflightError("DIRTY_REPOSITORY: commit all audit inputs before scanning")
    actual_commit = _git(repository, "rev-parse", "HEAD")
    if commit and actual_commit != commit:
        raise PreflightError("Requested commit does not match working tree")
    actual_branch = _git(repository, "branch", "--show-current") or "DETACHED"
    if branch and branch != actual_branch:
        raise PreflightError("Requested branch does not match working tree")
    paths = _git(repository, "ls-files", "-z").split("\0")
    files = []
    for relative in filter(None, paths):
        path = repository / relative
        if path.is_symlink() or not path.resolve().is_relative_to(repository):
            raise PreflightError("SYMLINK_NOT_SUPPORTED")
        if path.is_file():
            if path.stat().st_size > 1048576:
                raise PreflightError("FILE_SIZE_LIMIT")
            files.append(path)
    if len(files) > 10000:
        raise PreflightError("FILE_COUNT_LIMIT")
    java_files = [p for p in files if p.suffix == ".java"]
    frameworks = []
    if any("spring-boot" in p.read_text(encoding="utf-8", errors="ignore") for p in files if p.name in {"pom.xml", "build.gradle", "build.gradle.kts"}):
        frameworks.append("Spring Boot")
    if any("mybatis" in p.read_text(encoding="utf-8", errors="ignore").lower() for p in files if p.name in {"pom.xml", "build.gradle", "build.gradle.kts"}):
        frameworks.append("MyBatis")
    build_system = "Maven" if (repository / "pom.xml").exists() else "Gradle" if (repository / "build.gradle").exists() or (repository / "build.gradle.kts").exists() else "Unknown"
    if not java_files or "Spring Boot" not in frameworks or "MyBatis" not in frameworks:
        raise PreflightError("UNSUPPORTED_PROJECT")
    return {
        "repository": str(repository),
        "branch": actual_branch,
        "commit": actual_commit,
        "language": ["Java"] if java_files else [],
        "framework": frameworks,
        "build_system": build_system,
        "file_count": len(files),
        "scan_started_at": datetime.now(timezone.utc).isoformat(),
        "agent_version": agent_version,
        "rule_version": rule_version,
        "knowledge_version": knowledge_version,
    }


def file_digest(repository, relative):
    repository = Path(repository).resolve()
    path = (repository / relative).resolve()
    if not path.is_relative_to(repository) or not path.is_file():
        raise PreflightError("Evidence file is outside repository")
    return _sha256(path)
