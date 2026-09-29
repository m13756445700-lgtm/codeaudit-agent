"""Read-only capability layer. Navigation hints never become verdicts."""
import json
import re
from pathlib import Path
from agent.v2.repository import safe_path, files, digest
from agent.scanner.semgrep import scan

NAMES = ['repo.list_files', 'repo.tree', 'repo.read_file', 'repo.read_range', 'repo.search',
         'repo.find_symbol', 'repo.find_references', 'repo.find_callers', 'repo.find_callees',
         'repo.get_dependency', 'repo.get_route', 'repo.get_diff', 'code.call_graph',
         'dependency.inspect', 'static.semgrep', 'knowledge.retrieve']


class ToolLayer:
    def __init__(self, audit, knowledge=None, rules=None):
        self.audit = Path(audit)
        self.repo = self.audit / 'repo'
        self.metadata = json.loads((self.audit / 'metadata.json').read_text())
        self.knowledge = Path(knowledge or Path(__file__).resolve().parents[2] / 'knowledge' / 'v2')
        self.rules = Path(rules or Path(__file__).resolve().parents[2] / 'rules' / 'semgrep')

    def read(self, path, start=1, end=None):
        p = safe_path(self.repo, path)
        if path not in self.metadata['files'] or digest(p) != self.metadata['files'][path]:
            raise ValueError('Snapshot integrity failure')
        raw = p.read_bytes()
        if b'\0' in raw:
            return {'file': path, 'binary': True}
        lines = raw.decode('utf-8', errors='replace').splitlines()
        end = min(start + 119, len(lines)) if end is None else end
        if type(start) is not int or type(end) is not int or start < 1 or end < start or end > len(lines) or end - start >= 120:
            raise ValueError('Read range must exist and contain at most 120 lines')
        selected = [{'line': i + 1, 'code': lines[i][:2000]} for i in range(start - 1, end)]
        return {'file': path, 'sha256': digest(p), 'start': start, 'end': end, 'total_lines': len(lines),
                'lines': selected, 'truncated_lines': any(len(lines[i]) > 2000 for i in range(start - 1, end))}

    def call(self, name, arguments):
        if name not in NAMES or not isinstance(arguments, dict):
            raise ValueError('Unknown capability or invalid arguments')
        allowed = {'path', 'start', 'end', 'query', 'category', 'offset'}
        if set(arguments) - allowed:
            raise ValueError('Unknown tool argument')
        paths = sorted(self.metadata['files'])
        if name in ('repo.list_files', 'repo.tree'):
            offset = arguments.get('offset', 0)
            if type(offset) is not int or offset < 0:
                raise ValueError('Invalid offset')
            return {'files': paths[offset:offset+100], 'total': len(paths), 'next_offset': offset+100 if offset+100 < len(paths) else None}
        if name in ('repo.read_file', 'repo.read_range'):
            return self.read(arguments['path'], arguments.get('start', 1), arguments.get('end'))
        if name == 'knowledge.retrieve':
            category = arguments.get('category', '').lower()
            if not re.fullmatch('[a-z_]{2,40}', category):
                raise ValueError('Invalid knowledge category')
            p = safe_path(self.knowledge, category + '.md')
            if not p.is_file():
                return {'available': sorted(f.stem for f in self.knowledge.glob('*.md'))}
            return {'id': p.name, 'sha256': digest(p), 'content': p.read_text()[:12000]}
        if name == 'static.semgrep':
            candidates = scan(self.repo, self.rules, self.audit / 'static')
            return {'signals': [dict(c, type='candidate_signal', source='semgrep') for c in candidates[:80]],
                    'total': len(candidates), 'truncated': len(candidates) > 80,
                    'notice': 'Candidates only. No verdict. Inspect actual source, callers and defenses.'}
        if name == 'repo.get_diff':
            expected = self.metadata.get('revision_diff_sha256')
            if not expected:
                return {'available': False, 'reason': 'No Git revision baseline supplied for this input'}
            path = safe_path(self.audit, 'revision_diff.json')
            if digest(path) != expected:
                raise ValueError('Revision diff integrity failure')
            return json.loads(path.read_text())
        if name in ('repo.get_dependency', 'dependency.inspect'):
            matches = [p for p in paths if Path(p).name in ('pom.xml', 'requirements.txt', 'pyproject.toml', 'package.json', 'go.mod', 'build.gradle')]
            return {'dependency_files': matches, 'notice': 'Read manifests; dependency behavior not proven without source.'}
        query = arguments.get('query', '')
        if name == 'repo.get_route' and not query:
            queries = ['Mapping(', '@app.', 'router.', 'HandleFunc']
        else:
            if not isinstance(query, str) or not 1 <= len(query) <= 120:
                raise ValueError('Literal query required (1–120 chars)')
            queries = [query]
        hits = []
        for path in paths:
            raw = safe_path(self.repo, path).read_bytes()
            if b'\0' in raw:
                continue
            for i, line in enumerate(raw.decode('utf-8', errors='replace').splitlines(), 1):
                if any(q in line for q in queries):
                    hits.append({'file': path, 'line': i, 'code': line[:500]})
                    if len(hits) >= 80:
                        return {'matches': hits, 'truncated': True, 'method': 'lexical-navigation-not-resolved-call-graph'}
        return {'matches': hits, 'truncated': False, 'method': 'lexical-navigation-not-resolved-call-graph',
                'notice': 'Read definitions and call sites; textual matches do not establish reachability.'}


def main():
    import os
    import sys
    request = json.loads(sys.stdin.read(65537))
    audit_id = request['audit_id']
    if not re.fullmatch('[a-f0-9]{32}', audit_id):
        raise ValueError('Invalid audit id')
    audit = safe_path(Path(os.environ['CODEAUDIT_WORKSPACES']), audit_id)
    result = ToolLayer(audit).call(request['tool'], request['arguments'])
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
