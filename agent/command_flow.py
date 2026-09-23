"""Bounded static-call proof. Dynamic dispatch and ambiguous calls are unknown."""
from pathlib import Path
import javalang as j
from agent.evidence.model import reference

SPRING_IMPORTS = {'org.springframework.web.bind.annotation.RestController',
                  'org.springframework.web.bind.annotation.GetMapping',
                  'org.springframework.web.bind.annotation.RequestParam'}


def string_parameter(method):
    if len(method.parameters) != 1:
        return None
    p = method.parameters[0]
    if p.type.name != 'String' or p.type.dimensions or p.varargs:
        return None
    return p


def direct_endpoint(tree, cls, method):
    imports = {i.path for i in tree.imports if not i.static and not i.wildcard}
    p = string_parameter(method)
    return (SPRING_IMPORTS <= imports and [a.name for a in cls.annotations] == ['RestController']
            and method.modifiers == {'public'} and [a.name for a in method.annotations] == ['GetMapping']
            and p is not None and [a.name for a in p.annotations] == ['RequestParam'])


def static_method(cls, method):
    p = string_parameter(method)
    return (cls.modifiers == {'public', 'final'} and not cls.annotations and
            method.modifiers == {'public', 'static'} and not method.annotations and
            p is not None and not p.annotations and not method.type_parameters)


def trace_static_source(root, target_file, target_method, max_depth=6):
    """Find one unambiguous request-to-static-method chain, with byte references."""
    classes = {}
    for path in sorted(root.rglob('*.java')):
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            return None
        tree = j.parse.parse(path.read_text())
        for cls in tree.types:
            name = (tree.package.name + '.' if tree.package else '') + cls.name
            if name in classes:
                return None
            classes[name] = (tree, cls, path.relative_to(root).as_posix())
    targets = [name for name, (_, _, file) in classes.items() if file == target_file]
    if len(targets) != 1:
        return None

    def visit(target, method, visited):
        key = (target, method.name)
        if key in visited or len(visited) >= max_depth:
            return []
        _, target_cls, file = classes[target]
        if len([m for m in target_cls.methods if m.name == method.name]) != 1:
            return []
        parameter = string_parameter(method)
        if parameter is None:
            return []
        proofs = []
        for owner, (tree, cls, caller_file) in classes.items():
            if not isinstance(cls, j.tree.ClassDeclaration) or cls.extends or cls.implements or cls.fields or cls.type_parameters:
                continue
            if any(not isinstance(m, j.tree.MethodDeclaration) for m in cls.body):
                continue
            if any(i.static or i.wildcard for i in tree.imports):
                continue
            if any(i.path.rsplit('.',1)[-1] in {'String','Runtime','ProcessBuilder'} for i in tree.imports):
                continue
            for caller in cls.methods:
                p = string_parameter(caller)
                if p is None or caller.type_parameters or len(caller.body or []) != 1 or len([m for m in cls.methods if m.name == caller.name]) != 1:
                    continue
                statement = caller.body[0]
                if not isinstance(statement, j.tree.StatementExpression):
                    continue
                call = statement.expression
                if not isinstance(call, j.tree.MethodInvocation) or call.member != method.name or call.selectors or call.type_arguments or len(call.arguments) != 1:
                    continue
                if call.qualifier == p.name or not call.qualifier:
                    continue
                arg = call.arguments[0]
                if not isinstance(arg, j.tree.MemberReference) or arg.member != p.name or arg.qualifier or arg.selectors or arg.prefix_operators or arg.postfix_operators:
                    continue
                qualified = (tree.package.name + '.' if tree.package else '') + call.qualifier
                resolved = {name for name in classes if name == call.qualifier or name == qualified or any(i.path == name and name.rsplit('.',1)[-1] == call.qualifier for i in tree.imports)}
                if resolved != {target}:
                    continue
                call_ref = reference(root, caller_file, statement.position.line, symbol=p.name, type='STATIC_CALL_ARGUMENT')
                param_ref = reference(root, file, method.position.line, symbol=parameter.name, type='METHOD_PARAMETER')
                if direct_endpoint(tree, cls, caller):
                    source = reference(root, caller_file, caller.position.line, symbol=p.name, type='HTTP_REQUEST_PARAM')
                    proofs.append([source, call_ref, param_ref])
                elif static_method(cls, caller):
                    for prior in visit(owner, caller, visited | {key}):
                        proofs.append(prior + [call_ref, param_ref])
        return proofs

    proofs = visit(targets[0], target_method, set())
    return proofs[0] if len(proofs) == 1 else None
