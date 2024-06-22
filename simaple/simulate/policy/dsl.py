import functools
from typing import Callable, Generator

from simaple.simulate.policy.base import OperationGeneratorProto, PolicyContextType
from simaple.simulate.policy.parser import parse_dsl_to_operations

DSLGenerator = Generator[str, PolicyContextType, PolicyContextType]
DSLGeneratorProto = Callable[[PolicyContextType], DSLGenerator]


def interpret_dsl_generator(
    func: Callable[..., DSLGeneratorProto]
) -> Callable[..., OperationGeneratorProto]:
    @functools.wraps(func)
    def _gen_proto(*args, **kwargs):
        def _gen(ctx: PolicyContextType):
            dsl_cycle = func(*args, **kwargs)(ctx)
            dsl = next(dsl_cycle)  # pylint:disable=stop-iteration-return

            while True:
                ctx = yield parse_dsl_to_operations(dsl)
                dsl = dsl_cycle.send(ctx)

        return _gen

    return _gen_proto
