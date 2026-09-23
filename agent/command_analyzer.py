"""Bounded, fail-closed command proof for straight-line Spring endpoints.

Only explicit shell argv with tainted command text is verified. Single-string
Runtime.exec is deliberately inconclusive. No command in audited code is run.
"""
import json
from pathlib import Path
import javalang as j
from agent.evidence.model import reference
from agent.knowledge.loader import load
from agent.command_flow import direct_endpoint, static_method, trace_static_source, string_parameter


def analyze_command_candidate(repository, candidate, disabled_rules=()):
    root = Path(repository).resolve()
    ref = lambda line, symbol='', type='': reference(root, candidate['file'], line, symbol=symbol, type=type)
    unknown = {'category': 'COMMAND_INJECTION', 'kind': 'UNKNOWN',
               'sink': ref(candidate['line'], type='COMMAND_SINK')}
    try:
        result = _prove(root, candidate, ref, disabled_rules)
        return dict(result, category='COMMAND_INJECTION') if result else unknown
    except (ValueError, KeyError, TypeError, AttributeError, IndexError,
            j.parser.JavaSyntaxError, j.tokenizer.LexerError):
        return unknown


def _prove(root, candidate, ref, disabled_rules):
    tree = j.parse.parse((root / candidate['file']).read_text())
    knowledge, version = load(disabled_rules)
    required = ['KB-SPRING-REQUEST-PARAM', 'KB-JAVA-COMMAND-ARGV']
    if any(key not in knowledge for key in required):
        return None
    imports = {item.path for item in tree.imports if not item.static and not item.wildcard}
    if any(item.wildcard or item.static for item in tree.imports):
        return None
    if len(tree.types) != 1 or not isinstance(tree.types[0], j.tree.ClassDeclaration):
        return None
    cls = tree.types[0]
    # Keep annotation/type resolution unambiguous in this bounded implementation.
    if any(not isinstance(member, (j.tree.FieldDeclaration, j.tree.MethodDeclaration)) for member in cls.body):
        return None
    if cls.name in {'Runtime', 'ProcessBuilder', 'Map', 'String'} or cls.extends or cls.implements or cls.type_parameters:
        return None
    for path in root.rglob('*.java'):
        other = j.parse.parse(path.read_text())
        if any(t.name in {'Runtime', 'ProcessBuilder', 'Map', 'String',
                          'RestController', 'GetMapping', 'RequestParam'} for t in other.types):
            return None
    if any(i.rsplit('.', 1)[-1] in {'Runtime', 'ProcessBuilder', 'String'} for i in imports):
        return None

    def literal(node):
        if isinstance(node, j.tree.Literal) and not node.prefix_operators and not node.postfix_operators:
            value = json.loads(node.value)
            if isinstance(value, str):
                return value
        raise ValueError('Not a string literal')

    maps = {}
    for field in cls.fields:
        if field.modifiers != {'private', 'static', 'final'} or len(field.declarators) != 1:
            return None
        if field.type.name != 'Map' or 'java.util.Map' not in imports:
            return None
        decl = field.declarators[0]
        init = decl.initializer
        if not isinstance(init, j.tree.MethodInvocation) or init.qualifier != 'Map' or init.member != 'of' or init.selectors:
            return None
        values = [literal(a) for a in init.arguments]
        if not values or len(values) % 2 or len(set(values[::2])) != len(values[::2]):
            return None
        maps[decl.name] = ref(field.position.line, decl.name, 'IMMUTABLE_FINITE_MAPPING')
    proofs = []
    for method in cls.methods:
        param = string_parameter(method)
        if param is None or not method.body or method.type_parameters:
            continue
        if param.name in maps or param.name in {'Runtime', 'ProcessBuilder', 'Map'}:
            continue
        if direct_endpoint(tree, cls, method):
            source = ref(method.position.line, param.name, 'HTTP_REQUEST_PARAM')
            incoming = [source]
        elif static_method(cls, method):
            incoming = trace_static_source(root, candidate['file'], method)
            if not incoming:
                continue
            source = incoming[0]
        else:
            continue
        env = {param.name: ('TAINT', None, incoming)}

        def evaluate(node):
            if getattr(node, 'prefix_operators', None) or getattr(node, 'postfix_operators', None) or getattr(node, 'selectors', None):
                raise ValueError('Unsupported expression')
            if isinstance(node, j.tree.Literal):
                return ('CONST', literal(node), [])
            if isinstance(node, j.tree.MemberReference) and not node.qualifier:
                return env[node.member]
            if isinstance(node, j.tree.BinaryOperation) and node.operator == '+':
                a, b = evaluate(node.operandl), evaluate(node.operandr)
                if a[0] == b[0] == 'CONST':
                    return ('CONST', a[1] + b[1], [])
                if a[0] in {'CONST', 'TAINT'} and b[0] in {'CONST', 'TAINT'}:
                    return ('TAINT', None, a[2] + b[2])
            if isinstance(node, j.tree.MethodInvocation) and node.qualifier in maps and node.member == 'get' and len(node.arguments) == 1:
                arg = evaluate(node.arguments[0])
                if arg[0] == 'TAINT':
                    return ('MAPPED', None, arg[2] + [maps[node.qualifier]])
            raise ValueError('Unproven dataflow or protection')

        try:
            # Sink must be the final statement. Any branch or subsequent mutation fails closed.
            for statement in method.body[:-1]:
                if not isinstance(statement, j.tree.LocalVariableDeclaration) or statement.type.name != 'String' or statement.type.dimensions or len(statement.declarators) != 1:
                    raise ValueError('Unsupported statement')
                decl = statement.declarators[0]
                if decl.name in env or decl.name in maps or decl.name in {'Runtime', 'ProcessBuilder', 'Map'} or decl.dimensions:
                    raise ValueError('Ambiguous binding')
                value = evaluate(decl.initializer)
                env[decl.name] = (value[0], value[1], value[2] + [ref(statement.position.line, decl.name, 'LOCAL_ASSIGNMENT')])
            statement = method.body[-1]
            if not isinstance(statement, j.tree.StatementExpression) or statement.position.line != candidate['line']:
                continue
            call = statement.expression
            if isinstance(call, j.tree.MethodInvocation) and call.qualifier == 'Runtime' and call.member == 'getRuntime' and not call.arguments and len(call.selectors or []) == 1:
                execute = call.selectors[0]
                if execute.member != 'exec' or len(execute.arguments) != 1 or execute.selectors:
                    continue
                array = execute.arguments[0]
                if not isinstance(array, j.tree.ArrayCreator) or array.type.name != 'String' or not array.initializer or array.selectors:
                    continue
                args = array.initializer.initializers
            elif isinstance(call, j.tree.ClassCreator) and call.type.name == 'ProcessBuilder' and not call.body and len(call.selectors or []) == 1 and call.selectors[0].member == 'start' and not call.selectors[0].arguments and not call.selectors[0].selectors:
                args = call.arguments
            else:
                continue
            values = [evaluate(a) for a in args]
            if not values or values[0][0] != 'CONST':
                continue
            executable = values[0][1]
            shell = executable in {'sh', '/bin/sh', '/usr/bin/sh', 'bash', '/bin/bash', '/usr/bin/bash'}
            unsafe = shell and len(values) == 3 and values[1][:2] == ('CONST', '-c') and values[2][0] == 'TAINT'
            # Fixed approved utility; flags are not user controlled, mapped host is one argv entry.
            safe = (executable == '/usr/bin/ping' and len(values) == 4 and
                    values[1][:2] == ('CONST', '-c') and values[2][:2] == ('CONST', '1') and values[3][0] == 'MAPPED')
            if not (unsafe or safe):
                continue
            # Mapped values may not introduce utility option syntax.
            if safe:
                for field in cls.fields:
                    raw = field.declarators[0].initializer.arguments[1::2]
                    if any(not literal(a) or literal(a).startswith('-') for a in raw):
                        raise ValueError('Mapped option')
            sink = ref(statement.position.line, executable, 'EXPLICIT_SHELL_COMMAND' if unsafe else 'FIXED_EXECUTABLE_ARGV')
            inputs = [r for value in values for r in value[2]]
            argv = ref(statement.position.line, 'argv', 'COMMAND_ARGUMENT')
            flow = [source] + [r for r in inputs if r != source] + [argv, sink]
            # Parameter declaration is an explicit hop even without a local variable.
            if len(flow) < 4:
                flow.insert(1, ref(method.position.line, param.name, 'METHOD_PARAMETER'))
            proofs.append({'kind': 'UNSAFE' if unsafe else 'SAFE_ARGV', 'source': source, 'sink': sink,
                           'dataflow': flow, 'protection': {'status': 'ABSENT' if unsafe else 'VALID', 'evidence': flow},
                           'reachability': 'PRODUCTION_REACHABLE' if all(Path(r['file']).parts[:3] == ('src', 'main', 'java') for r in flow) else 'TEST_ONLY',
                           'rules_applied': required, 'knowledge_version': version})
        except (ValueError, KeyError, TypeError, AttributeError):
            continue
    return proofs[0] if len(proofs) == 1 else None
