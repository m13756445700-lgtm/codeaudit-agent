"""Route by controlled source format, never by a caller-provided verdict."""
from pathlib import Path
import javalang as j
from agent.evidence.model import reference
from agent.ssrf_analyzer import analyze_ssrf_candidate
from agent.path_analyzer import analyze_path_candidate
from agent.analyzer import analyze_sql_candidate
from agent.command_analyzer import analyze_command_candidate


def analyze_candidate(repository, candidate, disabled_rules=()):
    if Path(candidate['file']).suffix == '.java':
        # Classify the committed AST, never the caller's requested category.
        reference(repository, candidate['file'], candidate['line'])
        try:
            tree = j.parse.parse((Path(repository) / candidate['file']).read_text())
            if any(n.member == 'readString' and n.qualifier == 'Files' and n.position and n.position.line == candidate['line'] for _, n in tree.filter(j.tree.MethodInvocation)):
                return analyze_path_candidate(repository, candidate, disabled_rules)
            if any(n.member == 'getForObject' and n.position and n.position.line == candidate['line']
                   for _, n in tree.filter(j.tree.MethodInvocation)):
                return analyze_ssrf_candidate(repository, candidate, disabled_rules)
        except (j.parser.JavaSyntaxError, j.tokenizer.LexerError):
            pass
        return analyze_command_candidate(repository, candidate, disabled_rules)
    return analyze_sql_candidate(repository, candidate, disabled_rules)
