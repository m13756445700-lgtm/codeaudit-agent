"""Replay reviewed CPython string helpers from hash-pinned, operator-supplied sources.

No downloads, target imports, filesystem exploit, or Windows runtime claim.
"""
import argparse
import ast
import hashlib
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_directory', type=Path)
    args = parser.parse_args()
    print(json.dumps(replay(args.source_directory), indent=2))
