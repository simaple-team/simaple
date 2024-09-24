import math
from typing import cast

from lark import Lark, Transformer

__grammar = r"""
    ?start: expr

    ?expr: expr "+" term   -> add
         | expr "-" term   -> sub
         | term

    ?term: term "*" factor -> mul
         | term "/" factor -> div
         | term "//" factor -> int_div
         | term ">" factor  -> gt
         | term "<" factor -> lt
         | factor

    ?factor: NUMBER        -> number
           | SEPERATED_NUMBER -> seperated_number
           | "ceil(" expr ")" -> ceil
           | "floor(" expr ")" -> floor
           | "min(" expr "," expr ")" -> min
           | "max(" expr "," expr ")" -> max
           | VARIABLE -> variable
           | "-" factor    -> neg
           | "(" expr ")"

    SEPERATED_NUMBER: /[0-9_]+/
    VARIABLE: /[a-zA-Z_\.]+/
    %import common.NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""


class CalcTransformer(Transformer):
    def __init__(self, variables: dict[str, int | float]):
        self.variables = variables

    def variable(self, token):
        assert token[0].value in self.variables, f"Variable {token[0].value} is not defined"
        return self.variables[token[0].value]

    def number(self, token):
        return float(token[0])

    def seperated_number(self, token):
        return float(token[0].replace("_", ""))

    def add(self, items):
        return items[0] + items[1]

    def sub(self, items):
        return items[0] - items[1]

    def mul(self, items):
        return items[0] * items[1]

    def div(self, items):
        return items[0] / items[1]

    def int_div(self, items):
        return items[0] // items[1]

    def min(self, items):
        return min(items[0], items[1])

    def max(self, items):
        return max(items[0], items[1])

    def neg(self, items):
        return -items[0]

    def ceil(self, items):
        return math.ceil(items[0])

    def floor(self, items):
        return math.floor(items[0])

    def gt(self, items):
        return items[0] > items[1]

    def lt(self, items):
        return items[0] < items[1]


__arithmetic_parser = Lark(__grammar)


def evaluate_expression(expression, variables: dict[str, int | float]) -> int | float:
    ast = __arithmetic_parser.parse(expression)
    return cast(int | float, CalcTransformer(variables).transform(ast))
