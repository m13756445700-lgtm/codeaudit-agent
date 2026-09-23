"""Run BRD TC-01..12 against committed fixtures and actual Semgrep/Gate."""
import json
import shutil
import subprocess
from pathlib import Path
from agent.analysis import analyze_candidate
from agent.preflight import inventory
from agent.report import finalize_finding, validate_finding
from agent.scanner.semgrep import scan
from agent.knowledge.loader import load

ROOT=Path(__file__).resolve().parents[1]
XML='src/main/resources/mapper/UserMapper.xml'
MAPPING='''String field;
  switch(order) {
   case "name": field = "username"; break;
   case "time": field = "id"; break;
   default: field = "id"; break;
  }
  return mapper.raw(field);'''


def run(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    repositories={}
    for label,extra in [('sql',None),('allowlist',None),('command','CommandController'),('ssrf','FetchController'),('path','ReadController'),('test-only',None)]:
        repo=output/'repositories'/label
        shutil.copytree(ROOT/'fixtures/spring-security-lab',repo)
        if extra:
            folder={'command':'command-examples','ssrf':'ssrf-examples','path':'path-examples'}[label]
            shutil.copyfile(ROOT/'fixtures'/folder/(extra+'.java'),repo/'src/main/java/lab'/(extra+'.java'))
        if label=='allowlist':
            p=repo/'src/main/java/lab/UserService.java';p.write_text(p.read_text().replace('return mapper.raw(order);',MAPPING))
        if label=='test-only':
            p=repo/'src/main/java/lab/UserController.java'
            dest=repo/'src/test/java/lab/UserController.java';dest.parent.mkdir(parents=True);p.rename(dest)
        for args in [('init','-b','main'),('add','.'),('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-m','BRD acceptance fixture')]:
            subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True)
        manifest=inventory(repo)
        candidates=scan(repo,ROOT/'rules/semgrep',output/'scans'/label)
        repositories[label]=(repo,manifest,{(c['file'],c['line']) for c in candidates})
    cases=[('TC-01','sql',XML,5,'VERIFIED'),('TC-02','sql',XML,8,'REJECTED'),
           ('TC-03','allowlist',XML,5,'REJECTED'),('TC-04','sql',XML,5,'VERIFIED'),
           ('TC-05','command','src/main/java/lab/CommandController.java',12,'VERIFIED'),
           ('TC-06','command','src/main/java/lab/CommandController.java',22,'REJECTED'),
           ('TC-07','ssrf','src/main/java/lab/FetchController.java',13,'VERIFIED'),
           ('TC-08','ssrf','src/main/java/lab/FetchController.java',18,'REJECTED'),
           ('TC-09','path','src/main/java/lab/ReadController.java',14,'VERIFIED'),
           ('TC-10','path','src/main/java/lab/ReadController.java',28,'REJECTED'),
           ('TC-11','test-only',XML,5,'REJECTED'),('TC-12','allowlist',XML,5,'REJECTED')]
    rows=[]
    for case,label,file,line,expected in cases:
        repo,manifest,points=repositories[label]
        assert (file,line) in points,case+' candidate missing'
        finding=finalize_finding(analyze_candidate(repo,{'file':file,'line':line}),manifest,case)
        validate_finding(finding,ROOT/'schemas/finding.schema.json')
        assert finding['status']==expected,(case,finding['status'])
        if case=='TC-01':assert any(r['type']=='CALL_ARGUMENT' for r in finding['dataflow'])
        if case=='TC-04':assert finding['protection']['status']=='ABSENT'
        if case=='TC-11':assert finding['reachability']=='TEST_ONLY'
        details={'finding':finding}
        if case=='TC-12':
            disabled=('KB-MYBATIS-SQL-FP-ALLOWLIST',)
            other=finalize_finding(analyze_candidate(repo,{'file':file,'line':line},disabled),manifest,case,
                                   knowledge_version=load(disabled)[1],disabled_rules=disabled)
            validate_finding(other,ROOT/'schemas/finding.schema.json')
            assert other['status']=='NEEDS_REVIEW'
            assert other['knowledge_version']!=finding['knowledge_version']
            assert other['decision_trace']!=finding['decision_trace']
            details['disabled_finding']=other
        (output/(case+'.json')).write_text(json.dumps(details,indent=2))
        rows.append({'id':case,'pass':True,'repository':label,'commit':manifest['commit'],
                     'file':file,'line':line,'expected':expected,'actual':finding['status'],
                     'evidence':case+'.json','erratum':case in {'TC-05','TC-10'}})
    result={'passed':True,'cases':rows,'scope':'Static fixtures + real Semgrep + independent Gate; not Java execution or deployment acceptance'}
    (output/'matrix.json').write_text(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    result=run(args.output)
    print('BRD acceptance: %d/12 PASS'%len(result['cases']))
