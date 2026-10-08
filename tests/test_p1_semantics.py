"""Executable semantic reference checks; not a claim that an LLM reasons correctly."""
import ntpath
import posixpath
import pytest
from test_v2_tools_gate import context, finding
from agent.v2.gate import validate

@pytest.mark.parametrize('state',['supported','unknown','contradicted'])
def test_material_deployment_assumptions_cannot_be_confirmed(context,state):
    audit,meta,tools=context;receipts=[tools.read('app.py'),tools.read('db.py')];f=finding()
    f['environment_assumptions']=[{'claim':'Target Windows runtime','state':state,'references':[] if state=='unknown' else [f['sink']],'affects_verdict':True}]
    checked=validate(f,audit/'repo',meta,receipts,{})
    assert checked['status']=='INSUFFICIENT_EVIDENCE'

@pytest.mark.parametrize('state',['verified','supported','contradicted'])
def test_asserted_assumption_states_require_actual_references(context,state):
    audit,meta,tools=context;f=finding();f['environment_assumptions']=[{'claim':'Version2.1','state':state,'references':[],'affects_verdict':False}]
    assert not validate(f,audit/'repo',meta,[tools.read('app.py'),tools.read('db.py')],{})['evidence_gate']['passed']

def test_supported_conditional_claim_keeps_exact_precondition(context):
    audit,meta,tools=context;f=finding();claim='Target Windows runtime'
    f.update(judgment_scope='conditional_code',exploit_preconditions=[claim],environment_assumptions=[{'claim':claim,'state':'supported','references':[f['sink']],'affects_verdict':True}])
    assert validate(f,audit/'repo',meta,[tools.read('app.py'),tools.read('db.py')],{})['evidence_gate']['passed']

@pytest.mark.parametrize('path,windows,posix',[(r'C:\data\item',True,False),(r'\\host\share\item',True,False),('/srv/item',True,True),(r'folder\..\item',False,False)])
def test_path_flavors_are_not_interchangeable(path,windows,posix):
    assert ntpath.isabs(path)==windows
    assert posixpath.isabs(path)==posix

def test_mixed_separator_normalization():
    assert ntpath.normpath(r'a/b\..\c')==r'a\c'
    assert posixpath.normpath(r'a/b\..\c')==r'a/b\..\c'

@pytest.mark.parametrize('boundary',['framework','dependency'])
def test_sampled_versions_do_not_imply_unobserved_versions(boundary):
    # Explicit finite evidence model: no inference about all earlier/later versions.
    evidence={(boundary,'1.2.0'):'observed', (boundary,'1.2.2'):'observed'}
    assert evidence.get((boundary,'1.2.1'),'UNKNOWN')=='UNKNOWN'
    assert evidence.get((boundary,'2.0.0'),'UNKNOWN')=='UNKNOWN'

@pytest.mark.parametrize('placement,blocked', [('effective',True),('unreachable',False),('partial',False),('after_sink',False),('another_layer',True),('wrong_sanitizer',False)])
def test_guard_reference_scenarios(placement,blocked):
    events=[];input_value='a;bad'
    def guard(v):
        if ';' in v:raise ValueError('denied')
    def sink(v):events.append(v)
    try:
        if placement=='effective':guard(input_value)
        elif placement=='unreachable':
            if False:guard(input_value)
        elif placement=='partial':guard(input_value.split(';')[0])
        elif placement=='another_layer':
            def service(v):guard(v);sink(v)
            service(input_value);return
        elif placement=='wrong_sanitizer':input_value=input_value.replace('<','&lt;')
        sink(input_value)
        if placement=='after_sink':guard(input_value)
    except ValueError:pass
    assert (not events)==blocked
