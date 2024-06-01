import functools
import re
from typing import Callable, Generator

from simaple.simulate.policy.base import (
    Operation,
    OperationGeneratorProto,
    PolicyContextType,
)
from simaple.simulate.policy.parser import parse_dsl_to_operation


class DSLError(Exception):
    ...


class OperandDSLParser:
    def __call__(self, op_string: str) -> list[Operation]:
        try:
            mult = 1
            mult_match = re.compile(r"x([0-9]+) .*").match(op_string)
            if mult_match:
                mult = int(mult_match.group(1).strip())
                op_string = op_string.replace(f"x{mult_match.group(1)}", "")

            op = parse_dsl_to_operation(op_string)

            return [op for _ in range(mult)]
        except Exception as e:
            raise DSLError(str(e) + f" was {op_string}") from e


DSLGenerator = Generator[str, PolicyContextType, PolicyContextType]
DSLGeneratorProto = Callable[[PolicyContextType], DSLGenerator]


def interpret_dsl_generator(
    func: Callable[..., DSLGeneratorProto]
) -> Callable[..., OperationGeneratorProto]:
    @functools.wraps(func)
    def _gen_proto(*args, **kwargs):
        def _gen(ctx: PolicyContextType):
            dsl_cycle = func(*args, **kwargs)(ctx)
            parser = OperandDSLParser()

            dsl = next(dsl_cycle)  # pylint:disable=stop-iteration-return

            while True:
                ctx = yield parser(dsl)
                dsl = dsl_cycle.send(ctx)

        return _gen

    return _gen_proto
