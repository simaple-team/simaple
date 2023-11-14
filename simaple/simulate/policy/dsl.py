import functools
import re
from typing import Callable, Generator

from simaple.simulate.base import Client
from simaple.simulate.policy.base import (
    ConcreteSimulationHistory,
    Operation,
    OperationGeneratorProto,
    PolicyContextType,
    SimulationShell,
    _BehaviorGenerator,
)
from simaple.simulate.policy.operation import get_operations
from simaple.simulate.policy.parser import parse_dsl_to_operation


def dump(op: Operation) -> str:
    if op.name:
        if op.time:
            raise ValueError

        return f'{op.command}  "{op.name}"'

    return f"{op.command}  {op.time}"


class DSLError(Exception):
    ...


class OperandDSLParser:
    def __call__(self, op_string: str) -> list[Operation]:
        try:
            mult = 1
            mult_match = re.compile(r"x([0-9]+)  .*").match(op_string)
            if mult_match:
                mult = int(mult_match.group(1).strip())
                op_string = op_string.replace(mult_match.group(1), "")

            op = parse_dsl_to_operation(op_string)

            return [op for _ in range(mult)]
        except Exception as e:
            raise DSLError(str(e)) from e


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


class DSLShell(SimulationShell):
    def __init__(
        self,
        client: Client,
        handlers: dict[str, Callable[[Operation], _BehaviorGenerator]],
    ):
        super().__init__(client, handlers, ConcreteSimulationHistory())
        self._parser = OperandDSLParser()

    def exec_dsl(self, txt):
        ops = self._parser(txt)
        for op in ops:
            self.exec(op)

    def REPL(self):
        while True:
            txt = input(">> ")
            if txt == "exit":
                break

            if txt == "valid":
                print("-- valid skills --")
                for validity in self._client.show("validity"):
                    if validity.valid:
                        print(f"{validity.name}")
            elif txt == "running":
                for running in self._client.show("running"):
                    if running.time_left > 0:
                        print(f"{running.name} | {running.time_left}")
            else:
                try:
                    self.exec_dsl(txt)
                except DSLError as e:
                    print("Invalid DSL - try again")
                    print(f"Error Mesage: {e}")


def get_dsl_shell(client) -> DSLShell:
    return DSLShell(client, get_operations())
