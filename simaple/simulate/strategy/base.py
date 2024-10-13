from typing import Callable, Generator, Optional

from simaple.simulate.core.base import Event
from simaple.simulate.core.view import ViewerType
from simaple.simulate.engine import OperationEngine
from simaple.simulate.policy.base import Operation

RuntimeContextType = tuple[ViewerType, list[Event]]

OperationGenerator = Generator[Operation, RuntimeContextType, RuntimeContextType]
OperationGeneratorProto = Callable[[RuntimeContextType], OperationGenerator]


StrategyType = Callable[[RuntimeContextType], list[Operation]]


class PolicyWrapper:
    def __init__(self, operation_generator_proto: OperationGeneratorProto) -> None:
        self.operation_generator_proto = operation_generator_proto
        self._operation_generator: Optional[OperationGenerator] = None

    def __call__(self, context: RuntimeContextType) -> Operation:
        if self._operation_generator is None:
            self._operation_generator = self.operation_generator_proto(context)
            return next(self._operation_generator)

        return self._operation_generator.send(context)


def exec_by_strategy(
    engine: OperationEngine,
    policy: StrategyType,
) -> None:
    operations = policy((engine.get_current_viewer(), engine.get_buffered_events()))
    for op in operations:
        engine.exec(op)
