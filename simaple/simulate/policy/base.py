import abc
import functools
import hashlib
import json
from typing import Any, Callable, Generator, Optional, cast

from pydantic import BaseModel, PrivateAttr

from simaple.simulate.base import (
    Action,
    AddressedStore,
    Checkpoint,
    Client,
    Event,
    RouterDispatcher,
    ViewerType,
    ViewSet,
)
from simaple.simulate.report.base import Report
from simaple.simulate.report.dpm import DamageCalculator
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
    def __init__(self) -> None:
        self._logs: list[OperationLog] = [
            OperationLog(
                operation=Operation(command="init", name="init"),
                playlogs=[],
                previous_hash="",
            )
        ]

    def discard_after(self, idx: int) -> None:
        """Discard logs after idx."""
        self._logs = self._logs[: idx + 1]

    def get(self, idx: int) -> OperationLog:
        return self._logs[idx]

    def get_hash_index(self, log_hash: str) -> int:
        for idx, log in enumerate(self._logs[1:]):
            if log.previous_hash == log_hash:
                return idx

        if self._logs[-1].hash == log_hash:
            return len(self._logs)

        raise ValueError("No matching hash")

    def __len__(self) -> int:
        return len(self._logs)

    def __iter__(self):
        return iter(self._logs)

    def commit(
        self,
        operation: Operation,
        playlogs: list[PlayLog],
        checkpoint: Checkpoint,
    ):
        if len(self._logs) == 0:
            previous_hash = ""
        else:
            previous_hash = self._logs[-1].hash

        self._logs.append(
            OperationLog(
                operation=operation,
                playlogs=playlogs,
                checkpoint=checkpoint,
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


class SimulationShell:
    def __init__(
        self,
        client: Client,
        handlers: dict[str, Callable[[Operation], _BehaviorGenerator]],
    ):
        self._client = client
        self._viewset = client._viewset
        self._handlers = handlers
        self._buffered_events: list[Event] = []
        self._history = SimulationHistory()

    def save_history(self) -> dict[str, Any]:
        return self._history.save()

    def load_history(self, saved_history: dict[str, Any]) -> None:
        self._history.load(saved_history)
        self._client.load(self._history.get(-1).last().checkpoint.restore())

    def get_client(self) -> Client:
        return self._client

    def exec(self, op: Operation, early_stop: int = -1) -> None:
        playlogs: list[tuple[Action, list[Event], float]] = []

        for behavior in self.get_behavior_gen(op):
            if 0 < early_stop <= self._client.show("clock"):
                break
            action = behavior(self._buffered_events)
            if action is None:
                break
            self._buffered_events = self._client.play(action)
            playlogs.append(
                PlayLog(
                    action=action,
                    events=self._buffered_events,
                    clock=self._client.show("clock"),
                    checkpoint=self._client.save(),
                )
            )

        self._history.commit(
            op,
            playlogs,
            self._client.save(),
        )

    def get_behavior_gen(self, op: Operation) -> _BehaviorGenerator:
        return self._handlers[op.command](op)

    def exec_policy(self, policy: PolicyType, early_stop: int = -1) -> None:
        operations = policy(self.context)
        for op in operations:
            self.exec(op, early_stop=early_stop)

    @property
    def context(self):
        return (self._client.get_viewer(), self._buffered_events)

    def get_viewer(self, playlog: PlayLog) -> ViewerType:
        store, _ = playlog.checkpoint.restore()

        def _viewer(view_name: str) -> Any:
            return self._viewset.show(view_name, store)

        return _viewer

    def get_report(self, playlog: PlayLog) -> Report:
        viewer = self.get_viewer(playlog)
        report = Report()
        buff = viewer("buff")
        for event in playlog.events:
            if event["tag"] == Tag.DAMAGE:
                report.add(0, event, buff)

        return report

    def get(self, idx: int) -> OperationLog:
        return self._history.get(idx)

    def get_hash_index(self, log_hash: str) -> int:
        for idx, log in enumerate(self._history):
            if log.previous_hash == log_hash:
                return idx - 1

        if self._history.get(-1).hash == log_hash:
            return len(self._history) - 1

        raise ValueError("No matching hash")

    def rollback(self, idx: int):
        self._history.discard_after(idx)
        self._client.load(self._history.get(-1).last().checkpoint)

    def length(self) -> int:
        return len(self._history)

    """
    @abc.abstractmethod
    def get_viewer(self, playlog: PlayLog) -> ViewerType:
        ...

    @abc.abstractmethod
    def discard(self, idx: int) -> None:
        ...

    @abc.abstractmethod

    @abc.abstractmethod
    def get_hash_index(self, log_hash: str) -> int:
        ...

    @abc.abstractmethod
    def playlogs(self) -> Generator[PlayLog, None, None]:
        ...

    @abc.abstractmethod
    def get_report(self, playlog: PlayLog) -> Report:
        ...
    """
