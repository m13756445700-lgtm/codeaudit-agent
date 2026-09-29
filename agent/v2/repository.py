"""Bounded repository acquisition. Target code and build scripts never execute."""
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import time
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Limits:
    max_bytes: int = 50 * 1024 * 1024
    max_file: int = 1024 * 1024
    max_files: int = 5000
    clone_timeout: int = 90


SKIP = {'.git', 'node_modules', '.venv', '__pycache__', 'target', 'dist'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise ValueError('Invalid relative path')
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError('Path outside snapshot')
    root = Path(root).resolve()
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('Symlink is forbidden')
    if not current.resolve().is_relative_to(root):
        raise ValueError('Path outside snapshot')
    return current


def files(root):
    for parent, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        for d in dirs:
            if (Path(parent) / d).is_symlink():
                raise ValueError('Symlink is forbidden')
        for name in sorted(names):
            p = Path(parent) / name
            if p.is_symlink() or not p.is_file():
                raise ValueError('Only regular source files are allowed')
            yield p


def revision_diff(staging):
    """Capture bounded parent-to-HEAD changes without running external diff drivers."""
    parents = subprocess.check_output(
        ['git', '-C', str(staging), 'rev-list', '--parents', '-n', '1', 'HEAD'], timeout=10
    ).decode().split()
    command = ['git', '-C', str(staging), 'show', '--format=', '--root', '--no-ext-diff',
               '--no-textconv', '--no-renames', '--first-parent', '-m', '--unified=3', 'HEAD', '--']
    # Read only the bounded prefix; never spool an arbitrarily large patch to disk.
    import threading
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    chunks = []
    reader = threading.Thread(target=lambda: chunks.append(proc.stdout.read(12001)), daemon=True)
    reader.start()
    reader.join(timeout=10)
    timed_out = reader.is_alive()
    if (timed_out or (chunks and len(chunks[0]) > 12000)) and proc.poll() is None:
        proc.kill()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        proc.wait(timeout=5)
    reader.join(timeout=5)
    proc.stdout.close()
    if timed_out:
        return {'available': False, 'reason': 'Revision diff exceeded time budget'}
    patch = chunks[0]
    if proc.returncode and len(patch) <= 12000:
        raise ValueError('Cannot capture revision diff')
    return {'available': True, 'commit': parents[0],
            'base_commit': parents[1] if len(parents) > 1 else None,
            'comparison': 'first-parent' if len(parents) > 1 else 'initial-commit',
            'patch': patch[:12000].decode('utf-8', errors='replace'),
            'truncated': len(patch) > 12000,
            'notice': 'Diff is navigation evidence; read the current snapshot before security judgment.'}


def snapshot(source, workspaces, limits=Limits()):
    root = Path(workspaces).resolve()
    root.mkdir(parents=True, exist_ok=True)
    audit = root / uuid.uuid4().hex
    audit.mkdir(mode=0o700)
    repo, staging = audit / 'repo', audit / 'staging'
    repo.mkdir()
    count = total = 0
    manifest = {}

    def save(relative, content):
        nonlocal count, total
        target = safe_path(repo, relative)
        count += 1
        total += len(content)
        if count > limits.max_files or total > limits.max_bytes or len(content) > limits.max_file:
            raise ValueError('Repository resource limit exceeded')
        if target.exists():
            raise ValueError('Duplicate snapshot path')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        target.chmod(0o400)
        manifest[relative] = hashlib.sha256(content).hexdigest()

    try:
        source = str(source)
        kind = 'local'
        commit = None
        changes = None
        local = Path(source).expanduser()
        if source.startswith(('https://', 'http://', 'ssh://', 'git@')):
            kind = 'git'
            if source.startswith('git@') and not re.fullmatch(r'git@[A-Za-z0-9.-]+:[A-Za-z0-9._/-]+', source):
                raise ValueError('Invalid SSH Git URL')
            if not source.startswith('git@'):
                url = urlsplit(source)
                if url.password or (url.username and url.scheme != 'ssh') or url.query or url.fragment:
                    raise ValueError('Embedded credentials/query not permitted in Git URL')
            # No hooks, credential prompts, submodules, LFS or repository-supplied filters.
            env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GIT_LFS_SKIP_SMUDGE='1', GIT_CONFIG_NOSYSTEM='1')
            argv = ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'protocol.file.allow=never',
                    'clone', '--depth', '2', '--no-checkout', '--', source, str(staging)]
            proc = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
            deadline = time.monotonic() + limits.clone_timeout
            try:
                while proc.poll() is None:
                    size = sum(p.stat().st_size for p in staging.rglob('*') if p.is_file()) if staging.exists() else 0
                    if time.monotonic() > deadline or size > limits.max_bytes:
                        raise ValueError('Git clone time/size limit exceeded')
                    time.sleep(0.1)
                if proc.returncode:
                    raise ValueError('Git clone failed; check URL and external credentials')
            finally:
                if proc.poll() is None:
                    proc.kill()
                proc.wait()
            commit = subprocess.check_output(['git', '-C', str(staging), 'rev-parse', 'HEAD'], timeout=10).decode().strip()
            entries = subprocess.check_output(['git', '-C', str(staging), 'ls-tree', '-rz', 'HEAD'], timeout=10).split(b'\0')
            for entry in entries:
                if not entry:
                    continue
                meta, rawpath = entry.split(b'\t', 1)
                mode, typ, oid = meta.decode().split()
                if mode not in ('100644', '100755') or typ != 'blob':
                    raise ValueError('Git symlink/submodule unsupported; provide regular source snapshot')
                size = int(subprocess.check_output(['git', '-C', str(staging), 'cat-file', '-s', oid], timeout=10))
                if size > limits.max_file or total + size > limits.max_bytes or count >= limits.max_files:
                    raise ValueError('Repository resource limit exceeded')
                save(rawpath.decode('utf-8'), subprocess.check_output(['git', '-C', str(staging), 'cat-file', 'blob', oid], timeout=10))
            changes = revision_diff(staging)
        elif local.is_file() and zipfile.is_zipfile(local):
            kind = 'zip'
            with zipfile.ZipFile(local) as archive:
                if len(archive.infolist()) > limits.max_files:
                    raise ValueError('ZIP file count limit exceeded')
                for item in archive.infolist():
                    safe_path(repo, item.filename)
                    if stat.S_ISLNK(item.external_attr >> 16):
                        raise ValueError('ZIP symlink forbidden')
                    if item.is_dir():
                        continue
                    if item.file_size > limits.max_file or total + item.file_size > limits.max_bytes:
                        raise ValueError('ZIP expanded size limit exceeded')
                    save(item.filename, archive.read(item))
        elif local.is_dir() and not local.is_symlink():
            if root.is_relative_to(local.resolve()):
                raise ValueError('Workspace must be outside source repository')
            for path in files(local):
                if path.stat().st_size > limits.max_file:
                    raise ValueError('File size limit exceeded')
                save(path.relative_to(local).as_posix(), path.read_bytes())
        else:
            raise ValueError('Expected Git URL, ZIP or local directory')
        if not manifest:
            raise ValueError('Empty repository')
        shutil.rmtree(staging, ignore_errors=True)
        metadata = {'audit_id': audit.name, 'input_kind': kind, 'commit': commit, 'files': manifest,
                    'file_count': count, 'bytes': total,
                    'snapshot_sha256': hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()}
        if changes is not None:
            change_file = audit / 'revision_diff.json'
            change_file.write_text(json.dumps(changes, ensure_ascii=False))
            change_file.chmod(0o400)
            metadata['revision_diff_sha256'] = digest(change_file)
        (audit / 'metadata.json').write_text(json.dumps(metadata, indent=2))
        (audit / 'metadata.json').chmod(0o600)
        return audit, metadata
    except BaseException:
        shutil.rmtree(audit, ignore_errors=True)
        raise


def profile(repo):
    extensions = {'.java': 'Java', '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
                  '.tsx': 'TypeScript', '.go': 'Go', '.php': 'PHP', '.cs': 'C#', '.kt': 'Kotlin'}
    framework_signals = {'Spring': 'org.springframework', 'MyBatis': 'org.apache.ibatis', 'Flask': 'flask',
                         'FastAPI': 'fastapi', 'Django': 'django', 'Express': 'express', 'NestJS': '@nestjs',
                         'Next.js': 'next/', 'Go net/http': 'net/http', 'Gin': 'gin-gonic', 'Echo': 'labstack/echo'}
    surfaces = {'routes': ('Mapping(', '@app.', 'router.', 'HandleFunc'),
                'authentication': ('login', 'authenticate', 'jwt'), 'authorization': ('permission', 'authorize', 'role'),
                'database': ('execute(', 'query(', 'select ', 'jdbc'), 'filesystem': ('open(', 'readFile', 'Paths.'),
                'http_clients': ('requests.', 'http.Get', 'fetch(', 'RestTemplate'),
                'command_execution': ('exec(', 'ProcessBuilder', 'subprocess', 'os.system'),
                'serialization': ('pickle', 'deserialize', 'readObject'), 'templates': ('render_template', 'template'),
                'upload': ('upload', 'Multipart'), 'secrets': ('password', 'api_key', 'secret')}
    result = {'languages': {}, 'frameworks': [], 'files': [], 'dependencies': [], 'surface_hints': {},
              'mode': 'generic', 'audit_priorities': None}
    for p in files(repo):
        rel = p.relative_to(repo).as_posix()
        result['files'].append(rel)
        language = extensions.get(p.suffix)
        if language:
            result['languages'][language] = result['languages'].get(language, 0) + 1
        content = p.read_bytes()[:65536].decode('utf-8', errors='replace')
        for framework, token in framework_signals.items():
            if token in content and framework not in result['frameworks']:
                result['frameworks'].append(framework)
        for surface, tokens in surfaces.items():
            if any(token.lower() in content.lower() for token in tokens):
                result['surface_hints'].setdefault(surface, []).append(rel)
        if p.name in ('pom.xml', 'package.json', 'requirements.txt', 'pyproject.toml', 'go.mod', 'build.gradle'):
            result['dependencies'].append(rel)
    if result['languages']:
        result['mode'] = 'identified'
    result['note'] = 'Lexical navigation hints, not security conclusions. Priorities must be supplied by AI.'
    return result
