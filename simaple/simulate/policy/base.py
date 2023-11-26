import functools
import hashlib
import json
from typing import Any, Callable, Generator, Optional, cast

from pydantic import BaseModel, PrivateAttr

from simaple.simulate.base import Action, AddressedStore, Checkpoint, Event, ViewerType
from simaple.simulate.reserved_names import Tag


class Operation(BaseModel):
    """
    Operand is an aggregation of meaningful actions.
    An operand can contain one or more actions; This meant
    only operand-to-action translation is possible.
    """

    command: str
    name: str
    time: Optional[float] = None
    expr: str = ""


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
    >>>     events = engine.play(action)

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
        >>>     events = engine.play(action)
        """

        @functools.wraps(gen_method)
        def _wrapper(op: Operation):
            gen = cls(gen_method)
            return gen.handle(op)

        return _wrapper


PolicyContextType = tuple[ViewerType, list[Event]]

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


class PlayLog(BaseModel):
    clock: float

    action: Action
    events: list[Event]
    checkpoint: Checkpoint

    def get_delay_left(self) -> float:
        delay = 0
        for event in self.events:
            if event["tag"] in (Tag.DELAY,):
                if event["payload"]["time"] > 0:
                    delay += event["payload"]["time"]

        return delay


class OperationLog(BaseModel):
    operation: Operation
    playlogs: list[PlayLog]
    previous_hash: str
    _calculated_hash: Optional[str] = PrivateAttr(default=None)

    @property
    def hash(self) -> str:
        if not self._calculated_hash:
            stringified = self.previous_hash + json.dumps(
                self.model_dump(), sort_keys=True
            )
            self._calculated_hash = hashlib.sha1(stringified.encode()).hexdigest()

        return self._calculated_hash

    def last(self) -> PlayLog:
        return self.playlogs[-1]


class SimulationHistory:
    def __init__(
        self,
        initial_store: Optional[AddressedStore] = None,
        logs: Optional[list[OperationLog]] = None,
    ) -> None:
        assert not (logs is None and initial_store is None)
        if initial_store:
            self._logs: list[OperationLog] = [
                OperationLog(
                    operation=Operation(command="init", name="init"),
                    playlogs=[
                        PlayLog(
                            clock=0,
                            action={"name": "init", "method": "init", "payload": None},
                            events=[],
                            checkpoint=Checkpoint.create(initial_store),
                        )
                    ],
                    previous_hash="",
                )
            ]
        else:
            assert logs is not None
            self._logs = logs

    def discard_after(self, idx: int) -> None:
        """Discard logs after idx."""
        self._logs = self._logs[: idx + 1]

    def get(self, idx: int) -> OperationLog:
        return self._logs[idx]

    def __len__(self) -> int:
        return len(self._logs)

    def __iter__(self):
        return iter(self._logs)

    def commit(
        self,
        operation: Operation,
        playlogs: list[PlayLog],
    ):
        if len(self._logs) == 0:
            previous_hash = ""
        else:
            previous_hash = self._logs[-1].hash

        self._logs.append(
            OperationLog(
                operation=operation,
                playlogs=playlogs,
                previous_hash=previous_hash,
            )
        )

    def playlogs(self) -> Generator[PlayLog, None, None]:
        for log in self._logs:
            for playlog in log.playlogs:
                yield playlog

    def save(self) -> dict[str, Any]:
        return {
            "logs": [log.model_dump() for log in self._logs],
        }

    def load(self, saved_history) -> None:
        self._logs = [OperationLog.parse_obj(log) for log in saved_history["logs"]]

    def current_ckpt(self) -> Checkpoint:
        return self._logs[-1].last().checkpoint

    def shallow_copy(self) -> "SimulationHistory":
        return SimulationHistory(logs=list(self._logs))

    def show_ops(self) -> list[Operation]:
        return [playlog.operation for playlog in self]

    def get_hash_index(self, log_hash: str) -> int:
        for idx, log in enumerate(self._logs):
            if log.previous_hash == log_hash:
                return idx - 1

        if self._logs[-1].hash == log_hash:
            return len(self._logs) - 1

        raise ValueError("No matching hash")
