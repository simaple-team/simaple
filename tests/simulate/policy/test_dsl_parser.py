from simaple.simulate.policy.dsl import Operation
from simaple.simulate.policy.parser import parse_dsl_to_operations


def test_parse_use():
    result = parse_dsl_to_operations('USE "플레임 스윕" 200.0')
    assert result == [Operation(
        command="USE", name="플레임 스윕", time=200.0, expr='USE "플레임 스윕" 200.0'
    )]


def test_parse_cast():
    result = parse_dsl_to_operations('CAST "플레임 스윕"')
    assert result == [Operation(
        command="CAST", name="플레임 스윕", time=None, expr='CAST "플레임 스윕"'
    )]


def test_parse_elapse():
    result = parse_dsl_to_operations("ELAPSE 200.0")
    assert result == [Operation(
        command="ELAPSE", name="", time=200.0, expr="ELAPSE 200.0"
    )]


def test_parse_multiline():
    result = parse_dsl_to_operations(
        """
USE "플레임 스윕" 200.0
CAST "플레임 스윕"
ELAPSE 200.0
""".strip()
    )
    assert result == [
        Operation(
            command="USE", name="플레임 스윕", time=200.0, expr='USE "플레임 스윕" 200.0'
        ),
        Operation(
            command="CAST", name="플레임 스윕", time=None, expr='CAST "플레임 스윕"'
        ),
        Operation(command="ELAPSE", name="", time=200.0, expr="ELAPSE 200.0"),
    ]



def test_parse_multiline():
    result = parse_dsl_to_operations(
        """
USE "플레임 스윕" 200.0
CAST "플레임 스윕"
ELAPSE 200.0
""".strip()
    )
    assert result == [
        Operation(
            command="USE", name="플레임 스윕", time=200.0, expr='USE "플레임 스윕" 200.0'
        ),
        Operation(
            command="CAST", name="플레임 스윕", time=None, expr='CAST "플레임 스윕"'
        ),
        Operation(command="ELAPSE", name="", time=200.0, expr="ELAPSE 200.0"),
    ]
