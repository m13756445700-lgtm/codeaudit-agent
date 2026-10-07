"""Replay reviewed CPython string helpers from hash-pinned, operator-supplied sources.

No downloads, target imports, filesystem exploit, or Windows runtime claim.
"""
import argparse
import ast
import hashlib
import genericpath
import json
import os
from pathlib import Path


PINNED = {
    '3.11.1': 'ee9655fc0b3dd63aa8e583bb8cdcdd692e8d1cdcb347e1483475718f9a95ca3d',
    '3.11.2': '6dcebd56222c03c4c897938d0a153b3f164bbd2edf7474aaebf0fff7aee7d504',
}


def replay(directory: Path) -> dict:
    sources = []
    for version, digest in PINNED.items():
        path = directory / f'ntpath-{version}.py.txt'
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError(f'Source hash mismatch: {version}')
        tree = ast.parse(raw)
        names = {'isabs', 'splitdrive', '_get_bothseps'}
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
        if {n.name for n in functions} != names:
            raise ValueError(f'Missing reviewed helper: {version}')
        # Only these reviewed functions from these exact pinned files are compiled.
        namespace = {'os': os}
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), 'exec'), namespace)
        rows = []
        for value in ('//server/share', '//server/share/file', '\\\\server\\share'):
            rows.append({'path': value, 'splitdrive': list(namespace['splitdrive'](value)),
                         'isabs': namespace['isabs'](value)})
        sources.append({'version': version,
                        'url': f'https://raw.githubusercontent.com/python/cpython/v{version}/Lib/ntpath.py',
                        'sha256': digest, 'results': rows})
    return {'sources': sources, 'scope': 'CPython 3.11 adjacent-tag string-helper comparison only',
            'windows_runtime_test': False, 'filesystem_exposure_proven': False}


POSIX_SHA256 = '115bb3d2051318ee3d951cdb13c60f118f15cea837cb69fb52cf543c12fe25c3'


def replay_posix(directory: Path) -> dict:
    path = directory / 'posixpath-3.11.1.py.txt'
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != POSIX_SHA256:
        raise ValueError('Source hash mismatch: posixpath 3.11.1')
    tree = ast.parse(raw)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {'join', '_get_sep'}]
    # Select the reviewed pure-Python fallback; never execute imports or native helpers.
    for node in tree.body:
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                functions.extend(n for n in handler.body if isinstance(n, ast.FunctionDef) and n.name == 'normpath')
    if len(functions) != 3 or {n.name for n in functions} != {'join', '_get_sep', 'normpath'}:
        raise ValueError('Missing reviewed POSIX helpers')
    namespace = {'os': os, 'genericpath': genericpath}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), 'exec'), namespace)
    results = []
    for components in (['//server/share'], ['//server/share/file'], ['//server/share', 'file'], ['../file']):
        normalized = [namespace['normpath'](p) for p in components]
        results.append({'components': components, 'normalized': normalized,
                        'joined_if_guards_pass': namespace['join']('trusted-root', *normalized)})
    return {'url': 'https://raw.githubusercontent.com/python/cpython/v3.11.1/Lib/posixpath.py',
            'sha256': POSIX_SHA256, 'results': results,
            'scope': 'Reviewed string helpers including pure-Python normpath fallback; target guards not executed',
            'windows_runtime_test': False, 'filesystem_exposure_proven': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_directory', type=Path)
    parser.add_argument('--posix', action='store_true', help='Replay pinned POSIX normalization/join helpers instead')
    args = parser.parse_args()
    result = replay_posix(args.source_directory) if args.posix else replay(args.source_directory)
    print(json.dumps(result, indent=2))
