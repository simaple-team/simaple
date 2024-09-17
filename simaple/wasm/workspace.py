from typing import Any, Dict, cast

from simaple.container.cache import CachedCharacterProvider
from simaple.container.plan_metadata import PlanMetadata
from simaple.container.simulation import SimulationContainer
from simaple.simulate.policy.base import ConsoleText, Operation, is_console_command
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.wasm.base import return_js_object_from_pydantic_list
from simaple.wasm.models.simulation import OperationLogResponse


@return_js_object_from_pydantic_list
def run(
    plan: str,
    serialized_character_provider: dict[str, str],
) -> list[OperationLogResponse]:
    metadata_dict, op_or_consoles = parse_simaple_runtime(plan.strip())
    metadata = PlanMetadata.model_validate(metadata_dict)

    character_provider = CachedCharacterProvider.model_validate(
        serialized_character_provider
    )
    engine = SimulationContainer(
        metadata.simulation_setting, character_provider
    ).operation_engine()

    for op_or_console in op_or_consoles:
        if is_console_command(op_or_console):
            _ = engine.console(cast(ConsoleText, op_or_console))
            continue

        engine.exec(cast(Operation, op_or_console))

    return [
        OperationLogResponse.from_simulator(engine, log_index)
        for log_index in range(len(engine.history()))
    ]


def getSerializedCharacterProvider(
    plan: str,
) -> Dict[str, Any]:
    metadata_dict, _ = parse_simaple_runtime(plan.strip())
    metadata = PlanMetadata.model_validate(metadata_dict)

    character_provider = metadata.get_character_provider_config()

    prebuilt_character_provider = CachedCharacterProvider(
        cached_character=character_provider.character(),
        cached_simulation_config=character_provider.get_character_dependent_simulation_config(),
    )

    return prebuilt_character_provider.model_dump()
