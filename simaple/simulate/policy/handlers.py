import functools
from typing import Callable, Generator, Optional, cast

from simaple.simulate.base import Action, Event
from simaple.simulate.policy.base import Operation
from simaple.simulate.reserved_names import Tag

BehaviorGenerator = Generator[Callable[[list[Event]], Action], None, None]
ActionGeneratorType = Generator[Action, list[Event], None]


class BehaviorStrategy:
    """Generate Exec Op Runtime, and provides a generator interface to handle events.
    use case:
    >>> def exec_use(op, event: list[Event]) -> ExecOpType:
    >>>     ...
    >>> runtime = BehaviorStrategy(exec_use)
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
    ) -> BehaviorGenerator:
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


def get_next_elapse_time(events: list[Event]) -> float:
    for event in events:
        if event["tag"] in (Tag.DELAY,) and event["payload"]["time"] > 0:
            return event["payload"]["time"]  # type: ignore

    return 0.0


@BehaviorStrategy.operation_handler
def exec_cast(op: Operation, events: list[Event]) -> ActionGeneratorType:
    target_name = op.name

    action = dict(name=target_name, method="use", payload=None)
    events = yield action

    elapse_time = get_next_elapse_time(events)
    if elapse_time == 0:
        return

    yield dict(name="*", method="elapse", payload=elapse_time)


@BehaviorStrategy.operation_handler
def exec_use(op: Operation, events: list[Event]) -> ActionGeneratorType:
    _ = yield dict(name=op.name, method="use", payload=None)


@BehaviorStrategy.operation_handler
def exec_elapse(op: Operation, events: list[Event]) -> ActionGeneratorType:
    _ = yield dict(name="*", method="elapse", payload=op.time)


@BehaviorStrategy.operation_handler
def exec_resolve(op: Operation, events: list[Event]) -> ActionGeneratorType:
    elapse_time = get_next_elapse_time([ev for ev in events if ev["name"] == op.name])
    _ = yield dict(name="*", method="elapse", payload=elapse_time)


@BehaviorStrategy.operation_handler
def exec_keydownstop(op: Operation, events: list[Event]) -> ActionGeneratorType:
    _ = yield dict(name=op.name, method="stop", payload=None)


def get_operation_handlers() -> dict[
    str,
    Callable[[Operation], BehaviorGenerator],
]:
    return {
        "CAST": exec_cast,
        "USE": exec_use,
        "ELAPSE": exec_elapse,
        "KEYDOWNSTOP": exec_keydownstop,
        "RESOLVE": exec_resolve,
    }
