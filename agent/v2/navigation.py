"""Bounded Python AST navigation, never a reachability or taint verdict."""
import ast
from pathlib import Path
from agent.v2.repository import safe_path, digest


def navigate(repo, metadata, operation, query):
    definitions, calls, problems = [], [], []
    for path, expected in sorted(metadata['files'].items()):
        if not path.endswith('.py'):
            continue
        source = safe_path(repo, path)
        if digest(source) != expected:
            raise ValueError('Snapshot integrity failure')
        try:
            tree = ast.parse(source.read_text())
        except (SyntaxError, UnicodeError, RecursionError) as exc:
            problems.append({'file': path, 'reason': type(exc).__name__})
            continue
        # Conventional src layout: src is a source root unless it is a real package.
        module_path = path[4:] if path.startswith('src/') and 'src/__init__.py' not in metadata['files'] else path
        module = module_path[:-3].replace('/', '.')
        if module.endswith('.__init__'):
            module = module[:-9]
        imports = {}
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports[alias.asname or alias.name.split('.')[0]] = alias.name if alias.asname else alias.name.split('.')[0]
            elif isinstance(node, ast.ImportFrom):
                prefix = node.module or ''
                if node.level:
                    package = module.split('.') if Path(path).name == '__init__.py' else module.split('.')[:-1]
                    prefix = '.'.join(package[:len(package)-node.level+1] + ([prefix] if prefix else []))
                for alias in node.names:
                    if alias.name != '*':
                        imports[alias.asname or alias.name] = '.'.join(filter(None, [prefix, alias.name]))
        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.scope = []
            def visit_FunctionDef(self, node):
                qualified = '.'.join([module] + self.scope + [node.name])
                definitions.append({'symbol': qualified, 'name': node.name, 'file': path, 'line': node.lineno})
                self.scope.append(node.name)
                self.generic_visit(node)
                self.scope.pop()
            visit_AsyncFunctionDef = visit_FunctionDef
            def visit_ClassDef(self, node):
                self.scope.append(node.name)
                self.generic_visit(node)
                self.scope.pop()
            def visit_Call(self, node):
                expression = node.func
                parts = []
                while isinstance(expression, ast.Attribute):
                    parts.insert(0, expression.attr)
                    expression = expression.value
                if isinstance(expression, ast.Name):
                    parts.insert(0, expression.id)
                    literal = '.'.join(parts)
                    target = '.'.join([imports[parts[0]]] + parts[1:]) if parts[0] in imports else module + '.' + literal
                else:
                    literal, target = '<dynamic>', None
                calls.append({'caller': '.'.join([module] + self.scope), 'expression': literal,
                              'candidate': target, 'file': path, 'line': node.lineno})
                self.generic_visit(node)
        Visitor().visit(tree)
    from collections import Counter
    names = Counter(d['symbol'] for d in definitions)
    for call in calls:
        # Direct names/import aliases only. Dynamic dispatch/monkeypatching remain unproven.
        target = call.pop('candidate')
        call['callee'] = target if names[target] == 1 else None
        call['resolution'] = 'ambiguous' if names[target] > 1 else ('syntactic' if call['callee'] else 'unresolved')
    def match(value):
        return value and (value == query or value.endswith('.' + query))
    if operation == 'repo.find_symbol':
        matches = [d for d in definitions if match(d['symbol'])]
    elif operation == 'repo.find_callees':
        matches = [c for c in calls if match(c['caller'])]
    elif operation == 'repo.find_callers':
        matches = [c for c in calls if match(c['callee']) or match(c['expression'])]
    else:
        matches = [c for c in calls if match(c['caller']) or match(c['callee']) or match(c['expression'])]
    return {'matches': matches[:80], 'truncated': len(matches) > 80, 'parse_errors': problems[:20],
            'method': 'python-ast-import-navigation', 'languages': ['Python'],
            'notice': 'Syntactic candidates only; aliases can be rebound. Dynamic dispatch, closures and non-Python calls are unresolved. Read call sites and definitions; this is not reachability or taint proof.'}
