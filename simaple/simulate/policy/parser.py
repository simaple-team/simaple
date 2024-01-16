from typing import cast

from lark import Lark, Transformer

from simaple.simulate.policy.base import Operation

__PARSER = Lark(
    r"""
    operation: full_operation
          | time_operation
          | skill_operation
          | log_operation

    full_operation: op_command WS skill WS time
    time_operation: op_command WS time
    skill_operation: op_command WS skill
    log_operation: "!debug" WS expression

    op_command: WORD
    skill: ESCAPED_STRING
    time: SIGNED_NUMBER
    expression: ESCAPED_STRING

    %import common.WORD
    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS

    """,
    start="operation",
)


class TreeToOperation(Transformer):
    def op_command(self, s):
        (s,) = s
        return s.value

    def skill(self, s):
        (s,) = s
        return s[1:-1]

    def time(self, n):
        (n,) = n
        return float(n)

    def _no_ws(self, x):
        return [v for v in x if v]

    def WS(self, s):
        return None

    def operation(self, x):
        return x

    def full_operation(self, x):
        filter_out_x = self._no_ws(x)
        return Operation(
            command=filter_out_x[0],
            name=filter_out_x[1],
            time=filter_out_x[2],
        )

    def time_operation(self, x):
        filter_out_x = self._no_ws(x)
        return Operation(
            command=filter_out_x[0],
            name="",
            time=filter_out_x[1],
        )

    def skill_operation(self, x):
        filter_out_x = self._no_ws(x)
        return Operation(
            command=filter_out_x[0],
            name=filter_out_x[1],
            time=None,
        )

    def log_operation(self, x):
        _ws, wrapped_expression = x
        return Operation(
            command=wrapped_expression,
            name="",
            debug=True,
        )

    def expression(self, s):
        (s,) = s
        return s.value[1:-1]


__OperationTreeTransformer = TreeToOperation()


def get_parser():
    return __PARSER


def parse_dsl_to_operation(dsl: str) -> Operation:
    tree = __PARSER.parse(dsl)
    op = cast(Operation, __OperationTreeTransformer.transform(tree)[0])
    op.expr = dsl
    return op
