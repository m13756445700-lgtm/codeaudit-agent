"""Bounded AST proof: straight-line Java forwarding to an exact MyBatis mapper.

Unsupported expressions, branching, overloads and ambiguous types fail closed.
No finding is established merely by matching a variable name.
"""
import re
from pathlib import Path
import javalang as j
from agent.evidence.model import reference


def analyze_sql_candidate(repository, candidate, disabled_rules=()):
    root = Path(repository).resolve()
    sink = reference(root, candidate['file'], candidate['line'], type='SQL_SINK')
    unknown = {'kind': 'UNKNOWN', 'sink': sink}
    try:
        return _analyze(root, candidate, sink, disabled_rules) or unknown
    except (ValueError, KeyError, IndexError, AttributeError, j.parser.JavaSyntaxError, j.tokenizer.LexerError):
        return unknown


def _analyze(root, candidate, sink, disabled_rules):
    from agent.knowledge.loader import load
    knowledge, version = load(disabled_rules)
    # XML method/namespace are resolved structurally, with source line bounds.
    from defusedxml import ElementTree as ET
    path = root / candidate['file']
    if path.suffix != '.xml':
        return None
    xml = path.read_text()
    tree = ET.fromstring(xml)
    namespace = tree.attrib.get('namespace')
    blocks = list(re.finditer(r'<select\b[^>]*\bid="([^"]+)"[^>]*>(.*?)</select>', xml, re.S))
    matches = [b for b in blocks if xml[:b.start()].count('\n') + 1 <= candidate['line'] <= xml[:b.end()].count('\n') + 1]
    if len(matches) != 1:
        return None
    block = matches[0]
    sql = block.group(2)
    placeholders = re.findall(r'([#$])\{(\w+)\}', sql)
    if len(placeholders) != 1:
        return None
    marker, param = placeholders[0]
    sink = reference(root, candidate['file'], candidate['line'], symbol=param, type='MYBATIS_RAW_SUBSTITUTION' if marker == '$' else 'PARAMETER_BINDING')
    classes = {}
    for p in sorted(root.rglob('*.java')):
        if p.is_symlink() or not p.resolve().is_relative_to(root):
            return None
        parsed = j.parse.parse(p.read_text())
        for declaration in parsed.types:
            name = (parsed.package.name + '.' if parsed.package else '') + declaration.name
            if name in classes:
                return None
            classes[name] = (declaration, p.relative_to(root).as_posix(), parsed)
    if namespace not in classes:
        return None
    mapper, mapper_file, _ = classes[namespace]
    methods = [m for m in mapper.methods if m.name == block.group(1)]
    if len(methods) != 1 or len(methods[0].parameters) != 1:
        return None
    mp = methods[0].parameters[0]
    annotations = [a for a in mp.annotations if a.name == 'Param']
    if len(annotations) != 1 or not isinstance(annotations[0].element, j.tree.Literal) or annotations[0].element.value != '"' + param + '"':
        return None
    mapper_ref = reference(root, mapper_file, methods[0].position.line, symbol=mp.name, type='MAPPER_PARAMETER')

    def resolve_type(type_name, owner):
        _, _, parsed = classes[owner]
        names = [x for x in classes if x == type_name or x == (parsed.package.name + '.' + type_name if parsed.package else type_name) or any(i.path == x and x.endswith('.' + type_name) for i in parsed.imports)]
        return names[0] if len(names) == 1 else None

    mapping_evidence = []

    def follow(owner, method, symbol, visited):
        key = (owner, method.name)
        if key in visited or len(visited) >= 6:
            return None
        if not method.body:
            return None
        body = method.body
        if len(body) == 3 and isinstance(body[0], j.tree.LocalVariableDeclaration) and isinstance(body[1], j.tree.SwitchStatement):
            if 'KB-MYBATIS-SQL-FP-ALLOWLIST' not in knowledge:
                return None
            declaration, switch = body[:2]
            if len(declaration.declarators) != 1 or declaration.declarators[0].initializer is not None:
                return None
            mapped = declaration.declarators[0].name
            if not isinstance(switch.expression, j.tree.MemberReference) or switch.expression.member != symbol or switch.expression.qualifier:
                return None
            if not switch.cases or not any(not c.case for c in switch.cases):
                return None
            for case in switch.cases:
                if len(case.statements) != 2 or not isinstance(case.statements[0], j.tree.StatementExpression) or not isinstance(case.statements[1], j.tree.BreakStatement):
                    return None
                assignment = case.statements[0].expression
                if not isinstance(assignment, j.tree.Assignment) or assignment.type != '=' or not isinstance(assignment.expressionl, j.tree.MemberReference) or assignment.expressionl.member != mapped or assignment.expressionl.qualifier:
                    return None
                if not isinstance(assignment.value, j.tree.Literal) or not re.fullmatch(r'"[A-Za-z_][A-Za-z0-9_]*"', assignment.value.value):
                    return None
            symbol = mapped
            mapping_evidence.append(reference(root, classes[owner][1], declaration.position.line, body[-1].position.line, symbol=mapped, type='FINITE_MAPPING'))
            body = body[-1:]
        if len(body) != 1 or not isinstance(body[0], j.tree.ReturnStatement):
            return None
        call = body[0].expression
        if not isinstance(call, j.tree.MethodInvocation) or call.selectors or len(call.arguments) != 1:
            return None
        arg = call.arguments[0]
        if not isinstance(arg, j.tree.MemberReference) or arg.member != symbol or arg.qualifier or arg.selectors or arg.prefix_operators or arg.postfix_operators:
            return None
        decl, file, _ = classes[owner]
        fields = [f for f in decl.fields for d in f.declarators if d.name == call.qualifier and 'final' in f.modifiers]
        if len(fields) != 1:
            return None
        target = resolve_type(fields[0].type.name, owner)
        if not target:
            return None
        call_ref = reference(root, file, body[0].position.line, symbol=symbol, type='CALL_ARGUMENT')
        if target == namespace and call.member == block.group(1):
            return [call_ref, mapper_ref, sink]
        candidates = [m for m in classes[target][0].methods if m.name == call.member]
        if len(candidates) != 1 or len(candidates[0].parameters) != 1:
            return None
        downstream = follow(target, candidates[0], candidates[0].parameters[0].name, visited | {key})
        if downstream:
            declaration = reference(root, classes[target][1], candidates[0].position.line, symbol=candidates[0].parameters[0].name, type='METHOD_PARAMETER')
            return [call_ref, declaration] + downstream
        return None

    proofs = []
    for owner, (decl, file, _) in classes.items():
        if not any(a.name in ('RestController', 'Controller') for a in decl.annotations):
            continue
        for method in decl.methods:
            if not any(a.name in ('GetMapping', 'PostMapping', 'RequestMapping') for a in method.annotations) or len(method.parameters) != 1:
                continue
            parameter = method.parameters[0]
            if not any(a.name == 'RequestParam' for a in parameter.annotations):
                continue
            mapping_evidence.clear()
            flow = follow(owner, method, parameter.name, set())
            if flow:
                source = reference(root, file, method.position.line, symbol=parameter.name, type='HTTP_REQUEST_PARAM')
                excluded = any(part in {'test', 'examples', 'demo'} for part in Path(file).parts)
                required = 'KB-MYBATIS-SQL-BINDING' if marker == '#' else 'KB-MYBATIS-SQL-001'
                if required not in knowledge or 'KB-SPRING-REQUEST-PARAM' not in knowledge:
                    continue
                rules = ['KB-SPRING-REQUEST-PARAM', required]
                if mapping_evidence:
                    rules.append('KB-MYBATIS-SQL-FP-ALLOWLIST')
                proofs.append({'knowledge_version': version, 'rules_applied': rules, 'kind': 'SAFE_BINDING' if marker == '#' else 'UNSAFE', 'source': source, 'sink': sink, 'dataflow': [source] + flow, 'protection': {'status': 'VALID' if marker == '#' or mapping_evidence else 'ABSENT', 'evidence': [source] + list(mapping_evidence) + flow}, 'reachability': 'TEST_ONLY' if excluded else 'PRODUCTION_REACHABLE'})
    return proofs[0] if len(proofs) == 1 else None
