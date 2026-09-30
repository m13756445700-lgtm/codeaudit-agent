import pytest
from agent.v2.transport import OctoBus


def test_busy_retry_is_bounded_and_success_is_returned(monkeypatch):
    monkeypatch.setattr('agent.v2.transport.time.sleep', lambda _: None)
    transport = OctoBus.__new__(OctoBus)
    responses = iter([{'error':'SERVICE_BUSY'}, {'error':'CAPABILITY_HTTP_503'}, {'lines':[]}])
    transport._call = lambda *args: next(responses)
    assert transport.call('repo.read_file', {}) == {'lines':[]}
    calls=[]
    transport._call = lambda *args: calls.append(1) or {'error':'SERVICE_BUSY'}
    with pytest.raises(ValueError, match='SERVICE_BUSY'):
        transport.call('repo.read_file', {})
    assert len(calls) == 4


def test_invalid_request_is_not_retried_or_silently_accepted():
    transport = OctoBus.__new__(OctoBus)
    calls=[]
    transport._call = lambda *args: calls.append(1) or {'error':'CAPABILITY_HTTP_400'}
    with pytest.raises(ValueError, match='CAPABILITY_HTTP_400'):
        transport.call('repo.read_file', {})
    assert len(calls) == 1
