import abc
import functools
from typing import Callable, Generator, Optional, cast

from pydantic import BaseModel

from simaple.simulate.base import Action, Client, Environment, Event


class Operation(BaseModel):
    """
    Operand is an aggregation of meaningful actions.
    An operand can contain one or more actions; This meant
    only operand-to-action translation is possible.
    """

    command: str
    name: str
    time: Optional[float] = None


ActionGeneratorType = Generator[Action, list[Event], None]

_BehaviorGenerator = Generator[Callable[[list[Event]], Action], None, None]


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
        self, gen_method: Callable[[Operation, list[Event]], ActionGeneratorType]
    ):
        self._gen_method = gen_method
        self._gen: Optional[ActionGeneratorType] = None
        self._end: bool = False

    def handle(
        self,
        op: Operation,
    ) -> _BehaviorGenerator:
        self._op: Operation = op
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
    def operation_handler(
        cls, gen_method: Callable[[Operation, list[Event]], ActionGeneratorType]
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
        def _wrapper(op: Operation):
            gen = cls(gen_method)
            return gen.handle(op)

        return _wrapper


PolicyContextType = tuple[Environment, list[Event]]

OperationGenerator = Generator[Operation, PolicyContextType, PolicyContextType]
OperationGeneratorProto = Callable[[PolicyContextType], OperationGenerator]


PolicyType = Callable[[PolicyContextType], list[Operation]]


class PolicyWrapper:
    def __init__(self, operation_generator_proto: OperationGeneratorProto) -> None:
        self.operation_generator_proto = operation_generator_proto
        self._operation_generator: Optional[OperationGenerator] = None

    def __call__(self, context: PolicyContextType) -> Operation:
        if self._operation_generator is None:
            self._operation_generator = self.operation_generator_proto(context)
            return next(self._operation_generator)

        return self._operation_generator.send(context)


class OperationHistory(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def append(self, op: Operation) -> None:
        """Append operation to history"""

    def dump(self, file_name: str) -> None:
        """Dump history to file"""


class BaseOperationHistory(OperationHistory):
    def __init__(self) -> None:
        self._operations: list[Operation] = []

    def append(self, op: Operation) -> None:
        self._operations.append(op)

    def dump(self, file_name: str) -> None:
        with open(file_name, "w", encoding="utf-8") as f:
            for op in self._operations:
                f.write(str(op) + "\n")


class SimulationShell:
    def __init__(
        self,
        client: Client,
        handlers: dict[str, Callable[[Operation], _BehaviorGenerator]],
        history: OperationHistory,
    ):
        self._client = client
        self._handlers = handlers
        self._buffered_events: list[Event] = []
        self.history = history

    def exec(self, op: Operation, early_stop: int = -1) -> None:
        self.history.append(op)
        for behavior in self.get_behavior_gen(op):
            if 0 < early_stop <= self._client.show("clock"):
                break
            action = behavior(self._buffered_events)
            if action is not None:
                self._buffered_events = self._client.play(action)

    def get_behavior_gen(self, op: Operation) -> _BehaviorGenerator:
        return self._handlers[op.command](op)

    def exec_policy(self, policy: PolicyType, early_stop: int = -1) -> None:
        operations = policy(self.context)
        for op in operations:
            self.exec(op, early_stop=early_stop)

    @property
    def context(self):
        return (self._client.environment, self._buffered_events)
