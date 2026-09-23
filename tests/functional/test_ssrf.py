import copy
import shutil
import pytest
from test_pipeline import repo, git, ROOT
from agent.analysis import analyze_candidate
from agent.preflight import inventory
from agent.report import finalize_finding, validate_finding
from agent.validator.gate import evidence_gate
from agent.evidence.model import evidence_hash
from agent.scanner.semgrep import scan
from agent.service import dispatch
from agent.config import Config

FILE = 'src/main/java/lab/FetchController.java'

@pytest.fixture
def ssrf_repo(repo):
    shutil.copyfile(ROOT / 'fixtures/ssrf-examples/FetchController.java', repo / FILE)
    git(repo,'add','.')
    git(repo,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','SSRF fixture')
    return repo


def analyze(repo, line=13, disabled=()):
    return analyze_candidate(repo, {'file':FILE,'line':line}, disabled)

@pytest.mark.parametrize('line,status', [(13,'VERIFIED'),(18,'REJECTED'),(23,'NEEDS_REVIEW')])
def test_ssrf_verdicts(ssrf_repo,line,status):
    f=finalize_finding(analyze(ssrf_repo,line), inventory(ssrf_repo),'ssrf-test')
    validate_finding(f,ROOT/'schemas/finding.schema.json')
    assert f['category']=='SSRF'
    assert f['status']==status
    if status=='VERIFIED':
        assert all(f[x] for x in ('source','dataflow','sink','protection','reachability','evidence_integrity'))
        assert f['evidence_integrity']['status']=='PASS'

@pytest.mark.parametrize('old,new,line', [
    ('client.getForObject(url, String.class)', 'client.getForObject(filter(url), String.class)',13),
    ('client.getForObject(url, String.class)', 'client.getForObject("https://fixed.example.invalid", String.class)',13),
    ('new RestTemplate()', 'new RestTemplate(factory)',13),
    ('private final RestTemplate', 'private RestTemplate',13),
    ('org.springframework.web.client.RestTemplate', 'fake.RestTemplate',13),
    ('@RestController','@RestController @Profile("test")',13),
    ('public class FetchController {','public class FetchController { class RestTemplate {}',13),
    ('Map.of(', 'Map.copyOf(',18),
    ('private static final Map', 'private static Map',18),
    ('https://catalog.example.invalid/items', 'file:///etc/passwd',18),
    ('https://catalog.example.invalid/items', 'https://user:pass@catalog.example.invalid/items',18),
    ('SERVICES.get(serviceId)', 'serviceId + SERVICES.get(serviceId)',18),
    ('String url = SERVICES.get(serviceId);', 'String url = serviceId; url = SERVICES.get(serviceId);',18),
    ('String serviceId','String SERVICES',18),
])
def test_unproven_protection_or_types(ssrf_repo, old,new,line):
    p=ssrf_repo/FILE;p.write_text(p.read_text().replace(old,new))
    assert analyze(ssrf_repo,line)['kind']=='UNKNOWN'

@pytest.mark.parametrize('extra', [
    'public RestTemplate leak() { return client; }',
    'public void configure() { client.setInterceptors(null); }',
])
def test_mutated_or_escaped_client(ssrf_repo,extra):
    p=ssrf_repo/FILE;p.write_text(p.read_text().replace('public class FetchController {','public class FetchController { '+extra))
    assert analyze(ssrf_repo)['kind']=='UNKNOWN'


def test_mapping_rule_disabled(ssrf_repo):
    assert analyze(ssrf_repo,18,['KB-SPRING-SSRF-FIXED-MAPPING'])['kind']=='UNKNOWN'
    assert analyze(ssrf_repo,13,['KB-SPRING-SSRF-URL'])['kind']=='UNKNOWN'


def test_tampering_cannot_verify(ssrf_repo):
    value=finalize_finding(analyze(ssrf_repo),inventory(ssrf_repo),'ssrf-test')
    for key, replacement in [('category','COMMAND_INJECTION'),('source',None),('dataflow',[])]:
        bad=copy.deepcopy(value);bad[key]=replacement
        bad['evidence_integrity']['evidence_sha256']=evidence_hash(bad)
        assert evidence_gate(bad,ssrf_repo)[0]=='NEEDS_REVIEW'
    p=ssrf_repo/FILE;p.write_text(p.read_text().replace('client.getForObject(url, String.class)','client.getForObject("fixed", String.class)'))
    assert evidence_gate(value,ssrf_repo)[0]=='NEEDS_REVIEW'


def test_test_only_source(ssrf_repo):
    target=ssrf_repo/'src/test/java/lab/FetchController.java';target.parent.mkdir(parents=True)
    (ssrf_repo/FILE).rename(target)
    result=analyze_candidate(ssrf_repo,{'file':str(target.relative_to(ssrf_repo)),'line':13})
    assert result['reachability']=='TEST_ONLY'


def test_real_scan_and_controlled_service(ssrf_repo,tmp_path):
    candidates=scan(ssrf_repo,ROOT/'rules/semgrep',tmp_path/'scan')
    cases=[c for c in candidates if c['category']=='SSRF']
    assert {c['line'] for c in cases}=={13,18,23}
    config=Config(ssrf_repo.parent,tmp_path/'output')
    for c in cases:
        request={'repository':ssrf_repo.name,'commit':git(ssrf_repo,'rev-parse','HEAD'),'file':c['file'],'line':c['line']}
        f=dispatch('RunValidation',request,config)['result']
        assert f['status']=={13:'VERIFIED',18:'REJECTED',23:'NEEDS_REVIEW'}[c['line']]
