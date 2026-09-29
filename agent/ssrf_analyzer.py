"""Bounded SSRF proof for default RestTemplate and immutable URL mappings.

No network request is performed. Custom clients, guards and transformations
are inconclusive; fixed mapping proves only that input cannot choose a URL.
"""
import json
from pathlib import Path
from urllib.parse import urlsplit
import javalang as j
from agent.evidence.model import reference
from agent.knowledge.loader import load
from agent.command_flow import direct_endpoint, string_parameter


def analyze_ssrf_candidate(repository, candidate, disabled_rules=()):
    root = Path(repository).resolve()
    ref = lambda line, symbol='', type='': reference(root, candidate['file'], line, symbol=symbol, type=type)
    unknown = {'category': 'SSRF', 'kind': 'UNKNOWN', 'sink': ref(candidate['line'], type='HTTP_CLIENT')}
    try:
        return _prove(root, candidate, ref, disabled_rules) or unknown
    except (ValueError, KeyError, TypeError, AttributeError, IndexError,
            j.parser.JavaSyntaxError, j.tokenizer.LexerError):
        return unknown


def _prove(root, candidate, ref, disabled_rules):
    knowledge, version = load(disabled_rules)
    required = ['KB-SPRING-REQUEST-PARAM', 'KB-SPRING-SSRF-URL']
    if any(k not in knowledge for k in required):
        return None
    tree = j.parse.parse((root / candidate['file']).read_text())
    if len(tree.types) != 1 or not isinstance(tree.types[0], j.tree.ClassDeclaration):
        return None
    cls = tree.types[0]
    if cls.extends or cls.implements or cls.type_parameters:
        return None
    if any(not isinstance(n, (j.tree.FieldDeclaration, j.tree.MethodDeclaration)) for n in cls.body):
        return None
    imports = {i.path for i in tree.imports}
    if any(i.static or i.wildcard for i in tree.imports) or 'org.springframework.web.client.RestTemplate' not in imports:
        return None
    protected = {'RestTemplate', 'String', 'Map', 'RestController', 'GetMapping', 'RequestParam'}
    approved = {'org.springframework.web.client.RestTemplate', 'java.util.Map',
                'org.springframework.web.bind.annotation.RestController',
                'org.springframework.web.bind.annotation.GetMapping',
                'org.springframework.web.bind.annotation.RequestParam'}
    if any(i.rsplit('.', 1)[-1] in protected and i not in approved for i in imports):
        return None
    for path in root.rglob('*.java'):
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            return None
        other = j.parse.parse(path.read_text())
        if any(t.name in protected for _, t in other.filter(j.tree.TypeDeclaration)):
            return None

    def literal(node):
        if not isinstance(node, j.tree.Literal) or node.prefix_operators or node.postfix_operators or node.selectors:
            raise ValueError('Nonliteral')
        value = json.loads(node.value)
        if not isinstance(value, str):
            raise ValueError('Non-string')
        return value

    maps, clients = {}, {}
    for field in cls.fields:
        if len(field.declarators) != 1:
            return None
        decl = field.declarators[0]
        init = decl.initializer
        if field.type.dimensions or decl.dimensions:
            return None
        if field.type.name == 'RestTemplate' and field.modifiers == {'private', 'final'}:
            if not isinstance(init, j.tree.ClassCreator) or init.type.name != 'RestTemplate' or init.arguments or init.body or init.selectors:
                return None
            clients[decl.name] = ref(field.position.line, decl.name, 'DEFAULT_HTTP_CLIENT')
        elif field.type.name == 'Map' and field.modifiers == {'private', 'static', 'final'} and 'java.util.Map' in imports:
            if not isinstance(init, j.tree.MethodInvocation) or init.qualifier != 'Map' or init.member != 'of' or init.selectors:
                return None
            values = [literal(a) for a in init.arguments]
            if not values or len(values) % 2 or len(set(values[::2])) != len(values[::2]):
                return None
            for url in values[1::2]:
                parsed = urlsplit(url)
                if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password or parsed.fragment or parsed.query or any(c.isspace() or ord(c) < 32 for c in url):
                    return None
            maps[decl.name] = ref(field.position.line, decl.name, 'IMMUTABLE_SCHEME_HOST_MAPPING')
        else:
            return None
    if not clients:
        return None
    # The client must not be leaked, aliased, configured or mutated elsewhere.
    for _, node in cls.filter(j.tree.MemberReference):
        if node.member in clients:
            return None
    for _, node in cls.filter(j.tree.MethodInvocation):
        if node.qualifier in clients and node.member != 'getForObject':
            return None
    proofs = []
    for method in cls.methods:
        if not direct_endpoint(tree, cls, method) or method.type_parameters or not method.body:
            continue
        p = string_parameter(method)
        if p.name in clients or p.name in maps or p.name in protected:
            continue
        source = ref(method.position.line, p.name, 'HTTP_REQUEST_PARAM')
        env = {p.name: ('TAINT', [source])}

        def evaluate(node):
            if getattr(node, 'selectors', None) or getattr(node, 'prefix_operators', None) or getattr(node, 'postfix_operators', None):
                raise ValueError('Unknown transformation')
            if isinstance(node, j.tree.MemberReference) and not node.qualifier:
                return env[node.member]
            if isinstance(node, j.tree.MethodInvocation) and node.member == 'get' and node.qualifier in maps and len(node.arguments) == 1:
                kind, flow = evaluate(node.arguments[0])
                if kind == 'TAINT' and 'KB-SPRING-SSRF-FIXED-MAPPING' in knowledge:
                    return ('MAPPED', flow + [maps[node.qualifier]])
            raise ValueError('Unsupported value')

        try:
            for stmt in method.body[:-1]:
                if not isinstance(stmt, j.tree.LocalVariableDeclaration) or stmt.type.name != 'String' or stmt.type.dimensions or len(stmt.declarators) != 1:
                    raise ValueError('Unproven branch or guard')
                decl = stmt.declarators[0]
                if decl.name in env or decl.name in clients or decl.name in maps or decl.name in protected or decl.dimensions:
                    raise ValueError('Shadowing')
                kind, flow = evaluate(decl.initializer)
                env[decl.name] = (kind, flow + [ref(stmt.position.line, decl.name, 'LOCAL_ASSIGNMENT')])
            stmt = method.body[-1]
            if not isinstance(stmt, j.tree.ReturnStatement):
                continue
            call = stmt.expression
            if not isinstance(call, j.tree.MethodInvocation) or not call.position or call.position.line != candidate['line'] or call.member != 'getForObject' or call.qualifier not in clients or call.selectors or len(call.arguments) != 2:
                continue
            clazz = call.arguments[1]
            if not isinstance(clazz, j.tree.ClassReference) or clazz.type.name != 'String' or clazz.type.dimensions:
                continue
            kind, flow = evaluate(call.arguments[0])
            sink = ref(call.position.line, call.qualifier + '.getForObject', 'HTTP_CLIENT_URL')
            flow = flow + [ref(call.position.line, 'url', 'HTTP_URL_ARGUMENT'), sink]
            if len(flow) < 4:
                flow.insert(1, ref(method.position.line, p.name, 'METHOD_PARAMETER'))
            rules = required + (['KB-SPRING-SSRF-FIXED-MAPPING'] if kind == 'MAPPED' else [])
            proofs.append({'category': 'SSRF', 'kind': 'SAFE_MAPPING' if kind == 'MAPPED' else 'UNSAFE',
                'source': source, 'sink': sink, 'dataflow': flow,
                'protection': {'status': 'VALID' if kind == 'MAPPED' else 'ABSENT', 'evidence': [clients[call.qualifier]] + flow},
                'reachability': 'PRODUCTION_REACHABLE' if Path(candidate['file']).parts[:3] == ('src','main','java') else 'TEST_ONLY',
                'rules_applied': rules, 'knowledge_version': version})
        except (ValueError, KeyError, TypeError, AttributeError):
            continue
    return proofs[0] if len(proofs) == 1 else None
