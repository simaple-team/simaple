import functools
from contextlib import contextmanager
from typing import Callable, Generator, Literal, Union, Optional, TypeVar, cast, Type, Any
import re

from pydantic import BaseModel

from simaple.simulate.base import Action, Client, Environment, Event
from simaple.simulate.component.view import KeydownView, Running, Validity
from simaple.simulate.reserved_names import Tag

from abc import ABCMeta, abstractmethod


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


ExecOpType = Generator[Union[Action, None], tuple[list[Event], Environment], Union[Action, None]]
_BehaviorGenerator = Generator[Callable[[list[Event], Environment], Action], None, None]

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

    def __init__(
        self, gen_method: Callable[[OpVar, list[Event], Environment], ExecOpType]
    ):
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

    def __call__(self, events: list[Event], environment: Environment) -> Optional[Action]:
        if self._gen is None:
            self._gen = self._gen_method(self._op, events, environment)
            return next(self._gen)

        try:
            return self._gen.send((events, environment))
        except StopIteration as e:
            self._end = True
            return cast(Optional[Action], e.value)


    @classmethod
    def operation_handler(
        cls, gen_method: Callable[[OpVar, list[Event], Environment], ExecOpType]
    ):
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
def exec_cast(op: NamedOperation, events: list[Event], environment: Environment) -> ExecOpType:
    target_name = op.name

    action = Action(name=target_name, method="use")
    events, _ = yield action

    elapse_time = get_next_elapse_time(events)
    if elapse_time == 0:
        return None

    return Action(name="*", method="elapse", payload=elapse_time)



@BehaviorGenerator.operation_handler
def exec_use(op: NamedOperation, events: list[Event], environment: Environment) -> ExecOpType:
    _ = yield Action(name=op.name, method="use")
    return None


class TimeOperation(Operation):
    time: int

    def __str__(self) -> str:
        return f"{self.command}  {self.time}"

@BehaviorGenerator.operation_handler
def exec_elapse(
    op: TimeOperation, events: list[Event], environment: Environment
) -> ExecOpType:
    _ = yield Action(name="*", method="elapse", payload=op.time)
    return None


class KeydownOperation(NamedOperation):
    stopby: list[str]

    def __str__(self) -> str:
        return f"{self.command}  {self.name}  STOPBY  {'  '.join(self.stopby)}"


@BehaviorGenerator.operation_handler
def exec_keydown(
    op: KeydownOperation, events: list[Event], environment: Environment
) -> ExecOpType:
    target_name = op.name
    stopby = op.stopby

    if len(stopby) == 0:
        raise ValueError

    events, _ = yield Action(name=target_name, method="use")

    while True:
        elapse_time = get_next_elapse_time(events)
        if elapse_time == 0:
            break

        validities, runnings = validity_map(environment), running_map(environment)

        for name in stopby:
            if validities.get(name):
                if runnings.get(name, 0) > 0:
                    continue

                events, _ = yield Action(name=target_name, method="stop")
                while get_next_elapse_time(events) != 0:
                    events, _ = yield Action(
                        name="*", method="elapse", payload=get_next_elapse_time(events)
                    )

                return None

        events, environment = yield Action(
            name="*", method="elapse", payload=elapse_time
        )

    return Action(name=target_name, method="stop")


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
            op =  TimeOperation(
                command=command,
                time=int(argv[1]),
            )
        elif operation_type == KeydownOperation:
            op = KeydownOperation(
                command=command,
                name=argv[1],
                stopby=argv[3:],
            )
        else:
            raise ValueError

        return [
            op for _ in range(mult)
        ]

class SimulationInterpreter:
    def __init__(self, client: Client, handlers: dict[str, tuple[Any, Callable[[Operation], _BehaviorGenerator]]]):
        self._client = client
        self._handlers = handlers
        self._buffered_events: list[Event] = []

    def exec(self, op: Operation, early_stop: int = -1) -> None:
        for behavior in self.get_behavior_gen(op):
            action = behavior(self._buffered_events, self.environment)
            if action is not None:
                self._buffered_events = self._client.play(action)
            if 0 < early_stop <= self.environment.show("clock"):
                break

    def get_behavior_gen(self, op: Operation) -> _BehaviorGenerator:
        return self._handlers[op.command][1](op)

    @property
    def environment(self):
        return self._client.environment


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


def get_operations() -> dict[str, tuple[Type[Operation], Callable[[Operation, list[Event], Environment], ExecOpType]]]:
    return {
        "CAST": (NamedOperation, exec_cast),
        "USE": (NamedOperation, exec_use),
        "ELAPSE": (TimeOperation, exec_elapse),
        "KEYDOWN": (KeydownOperation, exec_keydown),
    }


def get_interpreter(client):
    return SimulationInterpreter(client, get_operations())


def get_operand_compiler() -> OperandCompiler:
    return OperandCompiler({
        k: v[0] for k, v in get_operations().items()
    })


class Policy(metaclass=ABCMeta):
    @abstractmethod
    def decide(self, environment: Environment) -> list[Operation]:
        """
        Decide next action based on current environment.
        """

class DSLBasedPolicy(Policy):
    def __init__(self) -> None:
        self._compiler = get_operand_compiler()

    @abstractmethod
    def decide_by_dsl(self, environment: Environment) -> str:
        """
        Decide next action based on current environment.
        """

    def decide(self, environment: Environment) -> list[Operation]:
        return self._compiler(self.decide_by_dsl(environment))
