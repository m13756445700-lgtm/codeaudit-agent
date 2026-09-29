"""Bounded request-to-file proof; unknown path guards fail closed."""
import json
from pathlib import Path
import javalang as j
from agent.command_flow import direct_endpoint, string_parameter
from agent.evidence.model import reference
from agent.knowledge.loader import load


def analyze_path_candidate(repository, candidate, disabled_rules=()):
    root = Path(repository).resolve()
    ref = lambda line, symbol='', type='': reference(root, candidate['file'], line, symbol=symbol, type=type)
    unknown = {'category':'PATH_TRAVERSAL','kind':'UNKNOWN','sink':ref(candidate['line'],type='FILE_READ')}
    try:
        return _prove(root,candidate,ref,disabled_rules) or unknown
    except (ValueError,KeyError,TypeError,AttributeError,IndexError,j.parser.JavaSyntaxError,j.tokenizer.LexerError):
        return unknown


def _prove(root,candidate,ref,disabled_rules):
    rules,version = load(disabled_rules)
    required = ['KB-SPRING-REQUEST-PARAM','KB-JAVA-PATH-READ']
    if any(k not in rules for k in required):
        return None
    tree=j.parse.parse((root/candidate['file']).read_text())
    if len(tree.types)!=1 or not isinstance(tree.types[0],j.tree.ClassDeclaration):return None
    cls=tree.types[0]
    if cls.extends or cls.implements or cls.type_parameters:return None
    if any(not isinstance(x,(j.tree.FieldDeclaration,j.tree.MethodDeclaration)) for x in cls.body):return None
    imports={i.path for i in tree.imports}
    if any(i.static or i.wildcard for i in tree.imports):return None
    if not {'java.nio.file.Files','java.nio.file.Paths'} <= imports:return None
    names={'Files','Paths','Path','String','SecurityException','RestController','GetMapping','RequestParam'}
    approved={'java.nio.file.Files','java.nio.file.Paths','java.nio.file.Path',
              'org.springframework.web.bind.annotation.RestController','org.springframework.web.bind.annotation.GetMapping',
              'org.springframework.web.bind.annotation.RequestParam'}
    if any(i.rsplit('.',1)[-1] in names and i not in approved for i in imports):return None
    for path in root.rglob('*.java'):
        if path.is_symlink() or not path.resolve().is_relative_to(root):return None
        parsed=j.parse.parse(path.read_text())
        if any(n.name in names for _,n in parsed.filter(j.tree.TypeDeclaration)):return None

    def literal(node):
        if not isinstance(node,j.tree.Literal) or node.prefix_operators or node.postfix_operators or node.selectors:raise ValueError('Nonliteral')
        value=json.loads(node.value)
        if not isinstance(value,str):raise ValueError('Not string')
        return value

    constants={}
    for field in cls.fields:
        if field.modifiers!={'private','static','final'} or field.type.name!='String' or field.type.dimensions or len(field.declarators)!=1:return None
        decl=field.declarators[0]
        if decl.dimensions:return None
        constants[decl.name]=('CONST',literal(decl.initializer),[ref(field.position.line,decl.name,'FIXED_BASE_STRING')])
    proofs=[]
    for method in cls.methods:
        if not direct_endpoint(tree,cls,method) or method.type_parameters or not method.body:continue
        p=string_parameter(method)
        if p.name in names or p.name in constants:continue
        source=ref(method.position.line,p.name,'HTTP_REQUEST_PARAM')
        env=dict(constants);env[p.name]=('TAINT',None,[source])
        if 'KB-JAVA-PATH-REAL-BOUNDARY' in rules:
            canonical = _canonical_proof(method, p.name, constants, imports, names, ref, source, candidate, required, version)
            if canonical:
                proofs.append(canonical)
                continue

        def evaluate(node):
            if getattr(node,'selectors',None) or getattr(node,'prefix_operators',None) or getattr(node,'postfix_operators',None):raise ValueError('Unknown transformation')
            if isinstance(node,j.tree.Literal):return ('CONST',literal(node),[])
            if isinstance(node,j.tree.MemberReference) and not node.qualifier:return env[node.member]
            if isinstance(node,j.tree.BinaryOperation) and node.operator=='+':
                a,b=evaluate(node.operandl),evaluate(node.operandr)
                if a[0]==b[0]=='CONST':return ('CONST',a[1]+b[1],a[2]+b[2])
                if a[0] in {'CONST','TAINT'} and b[0] in {'CONST','TAINT'}:return ('TAINT',None,a[2]+b[2])
            if isinstance(node,j.tree.MethodInvocation) and node.qualifier=='Paths' and node.member=='get' and len(node.arguments)==1:
                value=evaluate(node.arguments[0])
                if value[0]=='TAINT':return ('TAINT_PATH',None,value[2])
            raise ValueError('Unknown path or protection')
        try:
            for stmt in method.body[:-1]:
                if not isinstance(stmt,j.tree.LocalVariableDeclaration) or len(stmt.declarators)!=1 or stmt.type.name not in {'String','Path'} or stmt.type.dimensions:raise ValueError('Unproven statement or guard')
                if stmt.type.name=='Path' and 'java.nio.file.Path' not in imports:raise ValueError('Unknown Path type')
                decl=stmt.declarators[0]
                if decl.name in env or decl.name in names or decl.dimensions:raise ValueError('Shadowed binding')
                kind,value,flow=evaluate(decl.initializer)
                if kind=='TAINT_PATH' and stmt.type.name!='Path':raise ValueError('Type mismatch')
                if kind in {'CONST','TAINT'} and stmt.type.name!='String':raise ValueError('Type mismatch')
                env[decl.name]=(kind,value,flow+[ref(stmt.position.line,decl.name,'LOCAL_ASSIGNMENT')])
            stmt=method.body[-1]
            if not isinstance(stmt,j.tree.ReturnStatement):continue
            call=stmt.expression
            if not isinstance(call,j.tree.MethodInvocation) or call.qualifier!='Files' or call.member!='readString' or not call.position or call.position.line!=candidate['line'] or len(call.arguments)!=1 or call.selectors:continue
            kind,_,flow=evaluate(call.arguments[0])
            if kind!='TAINT_PATH':continue
            sink=ref(call.position.line,'Files.readString','FILE_READ_PATH')
            flow=flow+[ref(call.position.line,'path','FILE_PATH_ARGUMENT'),sink]
            if len(flow)<4:flow.insert(1,ref(method.position.line,p.name,'METHOD_PARAMETER'))
            proofs.append({'category':'PATH_TRAVERSAL','kind':'UNSAFE','source':source,'sink':sink,'dataflow':flow,
                'protection':{'status':'ABSENT','evidence':flow},
                'reachability':'PRODUCTION_REACHABLE' if Path(candidate['file']).parts[:3]==('src','main','java') else 'TEST_ONLY',
                'rules_applied':required,'knowledge_version':version})
        except (ValueError,KeyError,TypeError,AttributeError):continue
    return proofs[0] if len(proofs)==1 else None


def _canonical_proof(method, parameter, constants, imports, names, ref, source, candidate, required, version):
    """Exact four-statement real-path check; mutations and partial checks fail closed.

    Assumes the backing directory cannot be concurrently mutated by an attacker.
    This is a path-input proof, not a filesystem race or deployment attestation.
    """
    if len(method.body) != 4 or 'java.nio.file.Path' not in imports:
        return None
    base_stmt, target_stmt, guard, output = method.body

    def declaration(stmt):
        if not isinstance(stmt, j.tree.LocalVariableDeclaration) or stmt.type.name != 'Path' or stmt.type.dimensions or len(stmt.declarators) != 1:
            raise ValueError('Unknown path declaration')
        decl = stmt.declarators[0]
        if decl.dimensions or decl.name in names or decl.name in constants or decl.name == parameter:
            raise ValueError('Shadowed path binding')
        return decl.name, decl.initializer

    def member(node, name):
        return (isinstance(node, j.tree.MemberReference) and node.member == name and not node.qualifier
                and not node.selectors and not node.prefix_operators and not node.postfix_operators)

    def selector(node, name):
        return (isinstance(node, j.tree.MethodInvocation) and node.member == name and not node.arguments
                and not node.qualifier and not node.selectors and not node.type_arguments
                and not node.prefix_operators and not node.postfix_operators)

    try:
        base, init = declaration(base_stmt)
        if not isinstance(init, j.tree.MethodInvocation) or init.qualifier != 'Paths' or init.member != 'get' or len(init.arguments) != 1 or init.prefix_operators or init.postfix_operators:
            return None
        arg = init.arguments[0]
        if isinstance(arg, j.tree.Literal) and not arg.prefix_operators and not arg.postfix_operators:
            value = json.loads(arg.value)
            base_evidence = []
        elif isinstance(arg, j.tree.MemberReference) and member(arg, arg.member) and arg.member in constants:
            _, value, base_evidence = constants[arg.member]
        else:
            return None
        if not isinstance(value, str) or not value.startswith('/') or value == '/' or '\x00' in value or any(part in {'.', '..'} for part in value.split('/')):
            return None
        if len(init.selectors or []) != 1 or not selector(init.selectors[0], 'toRealPath'):
            return None
        target, resolve = declaration(target_stmt)
        if target == base or not isinstance(resolve, j.tree.MethodInvocation) or resolve.qualifier != base or resolve.member != 'resolve' or len(resolve.arguments) != 1 or not member(resolve.arguments[0], parameter) or resolve.prefix_operators or resolve.postfix_operators:
            return None
        selectors = resolve.selectors or []
        if not (len(selectors) == 1 and selector(selectors[0], 'toRealPath') or len(selectors) == 2 and selector(selectors[0], 'normalize') and selector(selectors[1], 'toRealPath')):
            return None
        if not isinstance(guard, j.tree.IfStatement) or guard.else_statement is not None:
            return None
        condition = guard.condition
        if not isinstance(condition, j.tree.MethodInvocation) or condition.qualifier != target or condition.member != 'startsWith' or condition.prefix_operators != ['!'] or condition.postfix_operators or condition.selectors or len(condition.arguments) != 1 or not member(condition.arguments[0], base):
            return None
        then = guard.then_statement
        statements = then.statements if isinstance(then, j.tree.BlockStatement) else [then]
        if len(statements) != 1 or not isinstance(statements[0], j.tree.ThrowStatement):
            return None
        thrown = statements[0].expression
        if not isinstance(thrown, j.tree.ClassCreator) or thrown.type.name != 'SecurityException' or thrown.arguments or thrown.body or thrown.selectors:
            return None
        if not isinstance(output, j.tree.ReturnStatement):
            return None
        call = output.expression
        if not isinstance(call, j.tree.MethodInvocation) or call.qualifier != 'Files' or call.member != 'readString' or not call.position or call.position.line != candidate['line'] or call.selectors or len(call.arguments) != 1 or not member(call.arguments[0], target):
            return None
        base_ref = ref(base_stmt.position.line, base, 'REAL_BASE_PATH')
        target_ref = ref(target_stmt.position.line, target, 'REAL_TARGET_PATH')
        guard_ref = ref(guard.position.line, target, 'REAL_PATH_BOUNDARY_THROW')
        sink = ref(call.position.line, 'Files.readString', 'FILE_READ_PATH')
        flow = [source, target_ref, ref(call.position.line, target, 'FILE_PATH_ARGUMENT'), sink]
        return {'category':'PATH_TRAVERSAL','kind':'SAFE_REAL_BOUNDARY','source':source,'sink':sink,'dataflow':flow,
                'protection':{'status':'VALID','evidence':base_evidence+[base_ref,target_ref,guard_ref,sink]},
                'reachability':'PRODUCTION_REACHABLE' if Path(candidate['file']).parts[:3]==('src','main','java') else 'TEST_ONLY',
                'rules_applied':required+['KB-JAVA-PATH-REAL-BOUNDARY'],'knowledge_version':version}
    except (ValueError, KeyError, TypeError, AttributeError):
        return None
