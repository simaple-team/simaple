from typing import cast

from simaple.container.cache import InMemoryCache
from simaple.container.plan_metadata import PlanMetadata
from simaple.simulate.policy.base import ConsoleText, Operation, is_console_command
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.wasm.base import (
    return_js_object_from_pydantic_list,
    return_js_object_from_pydantic_object,
)
from simaple.wasm.models.simulation import (
    FullOperationLogsWithCache,
    OperationLogResponse,
)


@return_js_object_from_pydantic_list
def runSimulatorWithPlanConfig(
    plan: str,
) -> list[OperationLogResponse]:
    metadata_dict, op_or_consoles = parse_simaple_runtime(plan.strip())
    metadata = PlanMetadata.model_validate(metadata_dict)

    engine = metadata.load_container().operation_engine()

    for op_or_console in op_or_consoles:
        if is_console_command(op_or_console):
            _ = engine.console(cast(ConsoleText, op_or_console))
            continue

        engine.exec(cast(Operation, op_or_console))

    return [
        OperationLogResponse.from_simulator(engine, log_index)
        for log_index in range(len(engine.history()))
    ]


@return_js_object_from_pydantic_object
def runSimulatorWithPlanConfigUsingCache(
    plan: str,
    cache: dict[str, str],
) -> FullOperationLogsWithCache:
    metadata_dict, op_or_consoles = parse_simaple_runtime(plan.strip())
    metadata = PlanMetadata.model_validate(metadata_dict)

    character_provider_cache = InMemoryCache(saved_cache=cache)
    engine = character_provider_cache.get_simulation_container(
        metadata.simulation_setting, metadata.get_character_provider_config()
    ).operation_engine()

    for op_or_console in op_or_consoles:
        if is_console_command(op_or_console):
            _ = engine.console(cast(ConsoleText, op_or_console))
            continue

        engine.exec(cast(Operation, op_or_console))

    return FullOperationLogsWithCache.model_construct(
        logs=[
            OperationLogResponse.from_simulator(engine, log_index)
            for log_index in range(len(engine.history()))
        ],
        cache=character_provider_cache.export(),
    )
