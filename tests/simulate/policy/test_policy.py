import pytest

from simaple.simulate.policy.base import TimeOperation, KeydownOperation, Operation, NamedOperation, get_operand_compiler


@pytest.mark.parametrize(
    "op, op_string",
    [
        (NamedOperation(command="USE", name="skill"), "USE  skill"),
        (NamedOperation(command="CAST", name="skill"), "CAST  skill"),
        (TimeOperation(command="ELAPSE", time=100), "ELAPSE  100"),
        (KeydownOperation(command="KEYDOWN", name="skill", stopby=["A", "B", "C"]), "KEYDOWN  skill  STOPBY  A  B  C"),
    ],
)
def test_operand_serializer(op, op_string):
    compiler = get_operand_compiler()
    assert compiler(op_string) == op
