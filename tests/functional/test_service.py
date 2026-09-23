import pytest
from test_pipeline import repo, XML, git
from agent.config import Config
from agent.service import dispatch

def test_controlled_methods(repo, tmp_path):
    config = Config(repo.parent, tmp_path / 'runs')
    request = {'repository':'lab', 'commit':git(repo,'rev-parse','HEAD'), 'file':XML, 'line':5}
    assert dispatch('InventoryRepository', {'repository':'lab'}, config)['result']['commit'] == request['commit']
    assert len(dispatch('ScanCandidates', {'repository':'lab','commit':request['commit']}, config)['result']['candidates']) == 2
    assert dispatch('ReadCodeSlice', request, config)['result']['snippet'].strip().startswith('SELECT')
    assert len(dispatch('HashEvidence', request, config)['result']['reference']['file_sha256']) == 64
    assert dispatch('RunValidation', request, config)['result']['status'] == 'VERIFIED'

def test_controlled_boundary(repo, tmp_path):
    config = Config(repo.parent, tmp_path / 'runs')
    for method, request in [('Shell', {}), ('InventoryRepository', {'repository':'../'}), ('InventoryRepository', {'repository':'lab','command':'id'}), ('ReadCodeSlice',{'repository':'lab','file':XML,'line':5})]:
        with pytest.raises(ValueError):
            dispatch(method, request, config)
