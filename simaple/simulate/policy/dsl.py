import functools
import re
from typing import Callable, Generator

from simaple.simulate.policy.base import (
    Operation,
    OperationGeneratorProto,
    PolicyContextType,
)


def parse(dsl: str) -> Operation:
    command, arg0 = dsl.strip().split("  ")
    name = ""
    time = 0.0
    if arg0.isdigit() or arg0.replace(".", "").isdigit():
        time = float(arg0)
    else:
        name = arg0

    return Operation(
        command=command,
        name=name,
        time=time,
    )


def dump(op: Operation) -> str:
    if op.name:
        if op.time:
            raise ValueError

        return f"{op.command}  {op.name}"

    return f"{op.command}  {op.time}"


class OperandDSLParser:
    def __call__(self, op_string: str) -> list[Operation]:
        mult = 1
        mult_match = re.compile(r"x([0-9]+)  .*").match(op_string)
        if mult_match:
            mult = int(mult_match.group(1).strip())
            op_string = op_string.replace(mult_match.group(1), "")

        op = parse(op_string)

        return [op for _ in range(mult)]

    def dump(self, op: Operation) -> str:
        return dump(op)


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
