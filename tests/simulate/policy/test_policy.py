import pytest

from simaple.simulate.policy.base import Operation
from simaple.simulate.policy.dsl import OperandDSLParser


@pytest.mark.parametrize(
    "op, op_string",
    [
        (Operation(command="USE", name="skill"), "USE  skill"),
        (Operation(command="CAST", name="skill"), "CAST  skill"),
        (Operation(command="ELAPSE", time=100, name=""), "ELAPSE  100"),
    ],
)
def test_operand_serializer(op, op_string):
    parser = OperandDSLParser()
    assert parser(op_string) == [op]
