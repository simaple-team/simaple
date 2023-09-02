import functools
import re
from typing import Callable, Generator, Optional

from simaple.simulate.policy.base import (
    Operation,
    OperationGeneratorProto,
    OperationHistory,
    PolicyContextType,
    SimulationShell,
)
from simaple.simulate.policy.operation import get_operations


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


class DSLOperationHistory(OperationHistory):
    def __init__(self) -> None:
        self._operations: list[Operation] = []

    def append(self, op: Operation) -> None:
        self._operations.append(op)

    def dump(self, file_name: str) -> None:
        with open(file_name, "w", encoding="utf-8") as f:
            previous_op: Optional[Operation] = None
            op_count = 0

            for op in self._operations:
                if previous_op is None:
                    previous_op = op
                    op_count = 1
                    continue

                if previous_op == op:
                    op_count += 1
                    continue

                if op_count > 1:
                    f.write(f"x{op_count} {dump(previous_op)}\n")
                else:
                    f.write(f"{dump(previous_op)}\n")

                previous_op = op
                op_count = 0
                continue
            
            assert previous_op is not None
            if op_count > 1:
                f.write(f"x{op_count} {dump(previous_op)}\n")
            else:
                f.write(f"{dump(previous_op)}\n")


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


def get_dsl_shell(client):
    return SimulationShell(client, get_operations(), DSLOperationHistory())
