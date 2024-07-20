import functools
from typing import Callable, Generator, Optional, cast

from simaple.simulate.base import Action, Event, ViewerType
from simaple.simulate.policy.base import Operation


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
