from simaple.simulate.policy.parser import parse_dsl_to_operation
from simaple.simulate.policy.dsl import Operation


def test_parse_use():
    result = parse_dsl_to_operation('USE "플레임 스윕" 200.0')
    assert result == Operation(command='USE', name='플레임 스윕', time=200.0)


def test_parse_cast():
    result = parse_dsl_to_operation('CAST "플레임 스윕"')
    assert result == Operation(command='CAST', name='플레임 스윕', time=None)


def test_parse_elapse():
    result = parse_dsl_to_operation('ELAPSE 200.0')
    assert result == Operation(command='ELAPSE', name='', time=200.0)
