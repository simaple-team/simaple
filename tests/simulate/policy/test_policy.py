import pytest

from simaple.simulate.policy.base import Operation
from simaple.simulate.policy.dsl import OperandDSLParser


@pytest.mark.parametrize(
    "op, op_string",
    [
        (
            Operation(command="USE", name="skill", time=None, expr='USE "skill"'),
            'USE "skill"',
        ),
        (
            Operation(command="CAST", name="skill", time=None, expr='CAST "skill"'),
            'CAST "skill"',
        ),
        (
            Operation(command="ELAPSE", time=100, name="", expr="ELAPSE 100"),
            "ELAPSE 100",
        ),
    ],
)
def test_operand_serializer(op, op_string):
    parser = OperandDSLParser()
    assert parser(op_string) == [op]
