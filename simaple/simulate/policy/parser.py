from typing import cast

import yaml
from lark import Discard, Lark, Token, Transformer
from pydantic import BaseModel

from simaple.simulate.policy.base import Operation


class ConsoleText(BaseModel):
    text: str


__PARSER = Lark(
    r"""
    simaple: (header WS? NEWLINE)? body

    body: (request|console) (NEWLINE (request|console))* 

    header: /\/\*(\*(?!\/)|[^*])*\*\//

    request: multiplier? WS? operation
    multiplier: "x" SIGNED_NUMBER

    operation: full_operation
          | time_operation
          | skill_operation

    full_operation: op_command WS skill WS time
    time_operation: op_command WS time
    skill_operation: op_command WS skill
    console: "!debug" WS expression

    op_command: WORD
    skill: ESCAPED_STRING
    time: SIGNED_NUMBER
    expression: ESCAPED_STRING

    MULTILINE_TEXT: /(.|\n)+/s

    %import common.WORD
    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS
    %import common.NEWLINE

    %ignore " "

    COMMENT: "#" /[^\n]/*
    %ignore COMMENT

    """,
    start=["body", "simaple"],
)


class TreeToOperation(Transformer):
    def simaple(self, tkns) -> tuple[dict, list[Operation | ConsoleText]]:
        if len(tkns) == 1:
            return {}, tkns[0]

        context, body = tkns
        return yaml.safe_load(context), body

    def header(self, tkns):
        assert len(tkns) == 1
        full_text = tkns[0]

        assert full_text[:2] == "/*"
        assert full_text[-2:] == "*/"
        context = full_text[2:-2]

        return context

    def op_command(self, command_word) -> str:
        (command,) = command_word
        return cast(str, command.value)

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

    def WS(self, white_space: Token):
        return Discard

    def NEWLINE(self, new_line: Token):
        return Discard

    def body(
        self, x: list[list[Operation] | list[ConsoleText]]
    ) -> list[Operation | ConsoleText]:
        return cast(list[Operation | ConsoleText], sum(x, []))

    def request(
        self,
        x: tuple[Operation,] | tuple[int, Operation],
    ) -> list[Operation]:
        if len(x) == 2:
            multiplier, operation = x
            return [operation for _ in range(multiplier)]

        return [cast(Operation, x[0])]

    def operation(
        self,
        x: tuple[Operation,],
    ) -> Operation:
        return x[0]

    def full_operation(self, x: tuple[str, str, float]) -> Operation:
        command, skill_name, time = x
        return Operation(
            command=command,
            name=skill_name,
            time=time,
            expr=f'{command} "{skill_name}" {time}',
        )

    def time_operation(self, x: tuple[str, float]) -> Operation:
        command, time = x
        return Operation(command=command, name="", time=time, expr=f"{command} {time}")

    def skill_operation(self, x: tuple[str, str]) -> Operation:
        command, skill_name = x
        return Operation(
            command=command,
            name=skill_name,
            time=None,
            expr=f'{command} "{skill_name}"',
        )

    def console(self, wrapped_expression: str) -> list[ConsoleText]:
        return [
            ConsoleText(
                text=wrapped_expression[0],
            )
        ]

    def expression(self, s):
        (s,) = s
        return s.value[1:-1]


__OperationTreeTransformer = TreeToOperation()


def get_parser():
    return __PARSER


class DSLError(Exception): ...


def is_console_command(op_or_console: ConsoleText | Operation) -> bool:
    return isinstance(op_or_console, ConsoleText)


def parse_dsl_to_operations(dsl: str) -> list[Operation]:
    try:
        ops = __OperationTreeTransformer.transform(__PARSER.parse(dsl, start="body"))
        assert all(isinstance(op, Operation) for op in ops)
        return cast(list[Operation], ops)
    except Exception as e:
        raise DSLError(str(e) + f" was {dsl}") from e


def parse_dsl_to_operations_or_console(dsl: str) -> list[ConsoleText | Operation]:
    try:
        return cast(
            list[ConsoleText | Operation],
            __OperationTreeTransformer.transform(__PARSER.parse(dsl, start="body")),
        )
    except Exception as e:
        raise DSLError(str(e) + f" was {dsl}") from e


def parse_simaple_runtime(
    runtime_text: str,
) -> tuple[dict, list[Operation | ConsoleText]]:
    operations = __OperationTreeTransformer.transform(
        __PARSER.parse(runtime_text.strip(), start="simaple")
    )
    return cast(tuple[dict, list[Operation | ConsoleText]], operations)
