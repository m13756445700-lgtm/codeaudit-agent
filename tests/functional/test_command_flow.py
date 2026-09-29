from pathlib import Path
import pytest
from test_pipeline import repo, git, ROOT
from agent.analysis import analyze_candidate
from agent.report import finalize_finding
from agent.preflight import inventory

FILE = 'src/main/java/lab/CommandRunner.java'
CONTROLLER = '''package lab;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
@RestController
public class CommandEndpoint {
    @GetMapping("/run")
    public void run(@RequestParam String input) throws Exception {
        CommandRunner.run(input);
    }
}
'''
RUNNER = '''package lab;
public final class CommandRunner {
    public static void run(String host) throws Exception {
        String cmd = "printf %s " + host;
        Runtime.getRuntime().exec(new String[]{"/bin/sh", "-c", cmd});
    }
}
'''

@pytest.fixture
def flow_repo(repo):
    (repo / 'src/main/java/lab/CommandEndpoint.java').write_text(CONTROLLER)
    (repo / FILE).write_text(RUNNER)
    return repo


def analyze(repo):
    return analyze_candidate(repo, {'file': FILE, 'line': 5})


def commit(repo):
    git(repo, 'add', '.')
    git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'flow')


def test_static_cross_file_proof_and_gate(flow_repo):
    commit(flow_repo)
    value = analyze(flow_repo)
    assert value['kind'] == 'UNSAFE'
    assert {r['type'] for r in value['dataflow']} >= {'HTTP_REQUEST_PARAM','STATIC_CALL_ARGUMENT','METHOD_PARAMETER','COMMAND_ARGUMENT'}
    assert value['source']['file'].endswith('CommandEndpoint.java')
    assert finalize_finding(value, inventory(flow_repo), 'flow')['status'] == 'VERIFIED'

@pytest.mark.parametrize('old,new', [
    ('CommandRunner.run(input)', 'CommandRunner.run("fixed")'),
    ('CommandRunner.run(input)', 'CommandRunner.run(filter(input))'),
    ('CommandRunner.run(input);', 'input = "fixed"; CommandRunner.run(input);'),
    ('CommandRunner.run(input)', 'Other.run(input)'),
    ('@RestController', '@RestController @Profile("test")'),
    ('String input', 'String CommandRunner'),
])
def test_unknown_caller_never_verifies(flow_repo, old, new):
    p = flow_repo / 'src/main/java/lab/CommandEndpoint.java'
    p.write_text(CONTROLLER.replace(old, new))
    assert analyze(flow_repo)['kind'] == 'UNKNOWN'

@pytest.mark.parametrize('old,new', [
    ('public static void', 'public void'),
    ('public final class', 'public class'),
    ('String cmd = "printf %s " + host;', 'String cmd = sanitize(host);'),
    ('public final class CommandRunner {', 'public final class CommandRunner { public static void run(int n) {}'),
])
def test_unknown_target_never_verifies(flow_repo, old, new):
    (flow_repo / FILE).write_text(RUNNER.replace(old,new))
    assert analyze(flow_repo)['kind'] == 'UNKNOWN'


def test_two_hop_static_chain(flow_repo):
    p = flow_repo / 'src/main/java/lab/CommandEndpoint.java'
    p.write_text(CONTROLLER.replace('CommandRunner.run(input)', 'CommandBridge.run(input)'))
    (p.parent / 'CommandBridge.java').write_text('''package lab;
public final class CommandBridge {
    public static void run(String value) throws Exception {
        CommandRunner.run(value);
    }
}
''')
    assert analyze(flow_repo)['kind'] == 'UNSAFE'
    assert any(r['file'].endswith('CommandBridge.java') for r in analyze(flow_repo)['dataflow'])


def test_test_caller_not_production(flow_repo):
    p = flow_repo / 'src/main/java/lab/CommandEndpoint.java'
    target = flow_repo / 'src/test/java/lab/CommandEndpoint.java'
    target.parent.mkdir(parents=True)
    p.rename(target)
    assert analyze(flow_repo)['reachability'] == 'TEST_ONLY'


def test_recursive_chain_unknown(flow_repo):
    p = flow_repo / 'src/main/java/lab/CommandEndpoint.java'
    p.write_text('package lab; public final class CommandEndpoint { public static void run(String input) throws Exception { CommandRunner.run(input); } }')
    assert analyze(flow_repo)['kind'] == 'UNKNOWN'
