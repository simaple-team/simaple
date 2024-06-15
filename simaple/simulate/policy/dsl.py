import functools
import re
from typing import Callable, Generator

from simaple.simulate.policy.base import (
    Operation,
    OperationGeneratorProto,
    PolicyContextType,
)
from simaple.simulate.policy.parser import parse_dsl_to_operations


class DSLError(Exception):
    ...


class OperandDSLParser:
    def __call__(self, op_string: str) -> list[Operation]:
        try:
            return parse_dsl_to_operations(op_string)
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
