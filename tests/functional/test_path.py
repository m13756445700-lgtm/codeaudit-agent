import copy
import shutil
import pytest
from test_pipeline import repo,git,ROOT
from agent.analysis import analyze_candidate
from agent.preflight import inventory
from agent.report import finalize_finding,validate_finding
from agent.validator.gate import evidence_gate
from agent.evidence.model import evidence_hash
from agent.scanner.semgrep import scan

FILE='src/main/java/lab/ReadController.java'
@pytest.fixture
def path_repo(repo):
    shutil.copyfile(ROOT/'fixtures/path-examples/ReadController.java',repo/FILE)
    git(repo,'add','.')
    git(repo,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','path fixture')
    return repo

def analyze(repo,line=14):
    return analyze_candidate(repo,{'file':FILE,'line':line})

def test_raw_path_six_evidence_gate(path_repo):
    f=finalize_finding(analyze(path_repo),inventory(path_repo),'path')
    validate_finding(f,ROOT/'schemas/finding.schema.json')
    assert f['category']=='PATH_TRAVERSAL'
    assert f['status']=='VERIFIED'
    assert all(f[k] for k in ('source','dataflow','sink','protection','reachability','evidence_integrity'))

def test_unimplemented_boundary_stays_unknown(path_repo):
    assert analyze(path_repo,21)['kind']=='UNKNOWN'

@pytest.mark.parametrize('old,new',[
    ('BASE_DIR + "/" + filename','BASE_DIR + "/fixed"'),
    ('BASE_DIR + "/" + filename','BASE_DIR + "/" + filename.replace("../", "")'),
    ('BASE_DIR + "/" + filename','BASE_DIR + "/" + filter(filename)'),
    ('String path =','filename = "fixed"; String path ='),
    ('java.nio.file.Files','fake.Files'),
    ('@RestController','@RestController @Profile("test")'),
    ('public class ReadController {','public class ReadController { class Files {}'),
    ('private static final String','private static String'),
    ('Paths.get(path)','Paths.get(other)'),
])
def test_unknown_paths_never_verify(path_repo,old,new):
    p=path_repo/FILE;p.write_text(p.read_text().replace(old,new))
    assert analyze(path_repo)['kind']=='UNKNOWN'

def test_tampered_path_evidence(path_repo):
    f=finalize_finding(analyze(path_repo),inventory(path_repo),'path')
    for key,value in [('category','SSRF'),('dataflow',[]),('source',None)]:
        bad=copy.deepcopy(f);bad[key]=value;bad['evidence_integrity']['evidence_sha256']=evidence_hash(bad)
        assert evidence_gate(bad,path_repo)[0]=='NEEDS_REVIEW'
    p=path_repo/FILE;p.write_text(p.read_text()+'\n')
    assert evidence_gate(f,path_repo)[0]=='NEEDS_REVIEW'

def test_disabled_path_knowledge(path_repo):
    assert analyze_candidate(path_repo,{'file':FILE,'line':14},['KB-JAVA-PATH-READ'])['kind']=='UNKNOWN'

def test_path_real_scanner(path_repo,tmp_path):
    results=scan(path_repo,ROOT/'rules/semgrep',tmp_path/'scan')
    assert {r['line'] for r in results if r['category']=='PATH_TRAVERSAL'}=={14,21,28}


def test_canonical_boundary_rejected(path_repo):
    value=finalize_finding(analyze(path_repo,28),inventory(path_repo),'path')
    validate_finding(value,ROOT/'schemas/finding.schema.json')
    assert value['status']=='REJECTED'
    assert {r['type'] for r in value['protection']['evidence']} >= {'REAL_BASE_PATH','REAL_TARGET_PATH','REAL_PATH_BOUNDARY_THROW'}

@pytest.mark.parametrize('old,new',[
    ('base.resolve(filename).toRealPath()', 'base.resolve(filename).normalize()'),
    ('Paths.get(BASE_DIR).toRealPath()', 'Paths.get(BASE_DIR).normalize()'),
    ('!target.startsWith(base)', 'target.startsWith(base)'),
    ('!target.startsWith(base)', '!target.toString().startsWith(base.toString())'),
    ('throw new SecurityException();', 'System.out.println("rejected");'),
    ('return Files.readString(target);', 'return Files.readString(Paths.get(filename));'),
    ('if (!target.startsWith(base))', 'target = base.resolve(filename); if (!target.startsWith(base))'),
    ('base.resolve(filename).toRealPath()', 'base.resolve(filename).toRealPath(LinkOption.NOFOLLOW_LINKS)'),
    ('"/srv/allowed"', '"/"'),
    ('"/srv/allowed"', '"/srv/../.."'),
])
def test_incomplete_or_bypassed_boundary_unknown(path_repo,old,new):
    p=path_repo/FILE;p.write_text(p.read_text().replace(old,new))
    assert analyze(path_repo,28)['kind']=='UNKNOWN'


def test_boundary_knowledge_disabled(path_repo):
    assert analyze_candidate(path_repo,{'file':FILE,'line':28},['KB-JAVA-PATH-REAL-BOUNDARY'])['kind']=='UNKNOWN'
