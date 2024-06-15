from typing import Any, cast

from lark import Discard, Lark, Token, Transformer

from simaple.simulate.policy.base import Operation

__PARSER = Lark(
    r"""
    multiplier: "x" SIGNED_NUMBER
    request: multiplier? WS? operation

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

    %ignore " "

    COMMENT: "#" /[^\n]/*
    %ignore COMMENT

    """,
    start="request",
)


class TreeToOperation(Transformer):
    def op_command(self, command_word) -> str:
        (command,) = command_word
        return command.value

    def skill(self, skill_string):
        """
        Extract skill name from double quote string
        """
        (skill_with_double_quote,) = skill_string
        return skill_with_double_quote[1:-1]

    def multiplier(self, multiplier_syntax) -> int:
        (multiplier_string,) = multiplier_syntax
        return int(multiplier_string)

    def time(self, time_signed_number) -> float:
        (time_string,) = time_signed_number
        return float(time_string)

    def _no_ws(self, x: list[str | None]) -> list[str]:
        return [v for v in x if v is not None]

    def WS(self, white_space: Token) -> None:
        return Discard

    def request(
        self,
        x: tuple[
            Operation,
        ]
        | tuple[int, Operation],
    ) -> tuple[Operation, int]:
        if len(x) == 2:
            multiplier, operation = x
        else:
            operation = x[0]
            multiplier = 1

        return operation, multiplier

    def operation(
        self,
        x: tuple[
            Operation,
        ],
    ) -> Operation:
        return x[0]

    def full_operation(self, x: tuple[str, str, float]) -> Operation:
        command, skill_name, time = x
        return Operation(
            command=command,
            name=skill_name,
            time=time,
        )

    def time_operation(self, x: tuple[str, float]) -> Operation:
        command, time = x
        return Operation(
            command=command,
            name="",
            time=time,
        )

    def skill_operation(self, x: tuple[str, str]) -> Operation:
        command, skill_name = x
        return Operation(
            command=command,
            name=skill_name,
            time=None,
        )

    def log_operation(self, wrapped_expression: str) -> Operation:
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


def parse_dsl_to_operations(dsl: str) -> list[Operation]:
    tree = __PARSER.parse(dsl)
    op, multiplier = __OperationTreeTransformer.transform(tree)
    op.expr = dsl
    return [op for _ in range(multiplier)]
