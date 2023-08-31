import functools
import re
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from typing import (
    Any,
    Callable,
    Generator,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

from pydantic import BaseModel

from simaple.simulate.base import Action, Client, Environment, Event
from simaple.simulate.component.view import KeydownView, Running, Validity
from simaple.simulate.reserved_names import Tag


def get_next_elapse_time(events: list[Event]) -> float:
    for event in events:
        if event.tag in (Tag.DELAY,) and event.payload["time"] > 0:
            return event.payload["time"]  # type: ignore

    return 0.0


def running_map(environment: Environment):
    runnings: list[Running] = environment.show("running")
    running_map = {r.name: r.time_left for r in runnings}
    return running_map


def validity_map(environment: Environment):
    validities: list[Validity] = environment.show("validity")
    validity_map = {v.name: v for v in validities if v.valid}
    return validity_map


class Operation(BaseModel):
    """
    Operand is an aggregation of meaningful actions.
    An operand can contain one or more actions; This meant
    only operand-to-action translation is possible.
    """

    class Config:
        extra = "forbid"

    command: str


ExecOpType = Generator[Action, list[Event], None]

_BehaviorGenerator = Generator[Callable[[list[Event]], Action], None, None]

OpVar = TypeVar("OpVar", bound=Operation)


class BehaviorGenerator:
    """Generate Exec Op Runtime, and provides a generator interface to handle events.
    use case:
    >>> def exec_use(op, event: list[Event]) -> ExecOpType:
    >>>     ...
    >>> runtime = BehaviorGenerator(exec_use)
    >>> for behavior in runtime.handle(op):
    >>>     action = behavior(events)
    >>>     events = client.play(action)

    """

    def __init__(self, gen_method: Callable[[OpVar, list[Event]], ExecOpType]):
        self._gen_method = gen_method
        self._gen: Optional[ExecOpType] = None
        self._end: bool = False

    def handle(
        self,
        op: OpVar,
    ) -> _BehaviorGenerator:
        self._op: OpVar = op
        while not self._end:
            yield self

    def __call__(self, events: list[Event]) -> Optional[Action]:
        if self._gen is None:
            self._gen = self._gen_method(self._op, events)
            return next(self._gen)

        try:
            return self._gen.send(events)
        except StopIteration as e:
            self._end = True
            return cast(Optional[Action], e.value)

    @classmethod
    def operation_handler(cls, gen_method: Callable[[OpVar, list[Event]], ExecOpType]):
        """Wraps Exec Op Runtime, and provides a generator interface to handle events.
        use case:
        >>> @BehaviorGenerator.operation_handler
        >>> def exec_use(op, event: list[Event]) -> ExecOpType:
        >>>     ...
        >>> for behavior in exec_use(op):
        >>>     action = behavior(events)
        >>>     events = client.play(action)
        """

        @functools.wraps(gen_method)
        def _wrapper(op: OpVar):
            gen = cls(gen_method)
            return gen.handle(op)

        return _wrapper


class NamedOperation(Operation):
    name: str

    def __str__(self) -> str:
        return f"{self.command}  {self.name}"


@BehaviorGenerator.operation_handler
def exec_cast(op: NamedOperation, events: list[Event]) -> ExecOpType:
    target_name = op.name

    action = Action(name=target_name, method="use")
    events = yield action

    elapse_time = get_next_elapse_time(events)
    if elapse_time == 0:
        return

    yield Action(name="*", method="elapse", payload=elapse_time)


@BehaviorGenerator.operation_handler
def exec_use(op: NamedOperation, events: list[Event]) -> ExecOpType:
    _ = yield Action(name=op.name, method="use")
    return


class TimeOperation(Operation):
    time: int

    def __str__(self) -> str:
        return f"{self.command}  {self.time}"


@BehaviorGenerator.operation_handler
def exec_elapse(op: TimeOperation, events: list[Event]) -> ExecOpType:
    _ = yield Action(name="*", method="elapse", payload=op.time)
    return


@BehaviorGenerator.operation_handler
def exec_keydownstop(op: NamedOperation, events: list[Event]) -> ExecOpType:
    _ = yield Action(name=op.name, method="stop")
    return


class KeydownOperation(NamedOperation):
    stopby: list[str]

    def __str__(self) -> str:
        return f"{self.command}  {self.name}  STOPBY  {'  '.join(self.stopby)}"


class OperandCompiler:
    def __init__(self, operations: dict[str, Operation]) -> None:
        self._operations = operations

    def __call__(self, op_string: str) -> list[Operation]:
        # Too many spaced skill name; therefore sep is 2 space.
        argv = op_string.strip().split("  ")
        mult = 1

        if re.compile(r"x[0-9]+").match(argv[0]):
            mult = int(argv[0][1:])
            argv = argv[1:]

        command = argv[0].upper()

        operation_type = self._operations[command]

        if operation_type == NamedOperation:
            op = NamedOperation(
                command=command,
                name=argv[1],
            )
        elif operation_type == TimeOperation:
            op = TimeOperation(
                command=command,
                time=int(float(argv[1])),
            )
        elif operation_type == KeydownOperation:
            op = KeydownOperation(
                command=command,
                name=argv[1],
                stopby=argv[3:],
            )
        else:
            raise ValueError

        return [op for _ in range(mult)]


class OperationRecorder:
    def __init__(self, file_name):
        self._file_name = file_name
        self._fp = None

    @contextmanager
    def start(self):
        with open(self._file_name, "w", encoding="utf-8") as fp:
            self._fp = fp
            yield self

    def write(self, operand: Operation):
        self._fp.write(f"{operand}\n")


def get_operations() -> dict[
    str, tuple[Type[Operation], Callable[[Operation, list[Event]], ExecOpType]]
]:
    return {
        "CAST": (NamedOperation, exec_cast),
        "USE": (NamedOperation, exec_use),
        "ELAPSE": (TimeOperation, exec_elapse),
        "KEYDOWNSTOP": (KeydownOperation, exec_keydownstop),
    }


def get_interpreter(client):
    return SimulationInterpreter(client, get_operations())


def get_operand_compiler() -> OperandCompiler:
    return OperandCompiler({k: v[0] for k, v in get_operations().items()})


PolicyContextType = tuple[Environment, list[Event]]

OperationGenerator = Generator[Operation, PolicyContextType, PolicyContextType]
OperationGeneratorProto = Callable[[PolicyContextType], OperationGenerator]
DSLGenerator = Generator[str, PolicyContextType, PolicyContextType]
DSLGeneratorProto = Callable[[PolicyContextType], DSLGenerator]


def interpret_dsl_generator(
    func: Callable[..., DSLGeneratorProto]
) -> Callable[..., OperationGeneratorProto]:
    @functools.wraps(func)
    def _gen_proto(*args, **kwargs):
        def _gen(ctx: PolicyContextType):
            dsl_cycle = func(*args, **kwargs)(ctx)
            compiler = get_operand_compiler()

            dsl = next(dsl_cycle)

            while True:
                ctx = yield compiler(dsl)
                dsl = dsl_cycle.send(ctx)

        return _gen

    return _gen_proto


PolicyType = Callable[[PolicyContextType], list[Operation]]


class PolicyWrapper:
    def __init__(self, operation_generator_proto: OperationGeneratorProto) -> None:
        self.operation_generator_proto = operation_generator_proto
        self._operation_generator: Optional[OperationGenerator] = None

    def __call__(self, context: PolicyContextType) -> list[Operation]:
        if self._operation_generator is None:
            self._operation_generator = self.operation_generator_proto(context)
            return next(self._operation_generator)

        return self._operation_generator.send(context)


class SimulationInterpreter:
    def __init__(
        self,
        client: Client,
        handlers: dict[str, tuple[Any, Callable[[Operation], _BehaviorGenerator]]],
    ):
        self._client = client
        self._handlers = handlers
        self._buffered_events: list[Event] = []

    def exec(self, op: Operation, early_stop: int = -1) -> None:
        for behavior in self.get_behavior_gen(op):
            action = behavior(self._buffered_events)
            if action is not None:
                self._buffered_events = self._client.play(action)
            if 0 < early_stop <= self.environment.show("clock"):
                break

    def get_behavior_gen(self, op: Operation) -> _BehaviorGenerator:
        return self._handlers[op.command][1](op)

    def exec_policy(self, policy: PolicyType, early_stop: int = -1) -> None:
        operations = policy(self.context)
        for op in operations:
            self.exec(op, early_stop=early_stop)
            if 0 < early_stop <= self.environment.show("clock"):
                break

    @property
    def context(self):
        return (self._client.environment, self._buffered_events)

    @property
    def environment(self):
        return self._client.environment
