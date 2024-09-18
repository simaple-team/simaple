from typing import Any, Dict, cast

from simaple.container.cache import CachedCharacterProvider
from simaple.container.plan_metadata import PlanMetadata
from simaple.simulate.policy.base import ConsoleText, Operation, is_console_command
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.simulate.report.base import DamageLog
from simaple.wasm.base import return_js_object_from_pydantic_list
from simaple.wasm.models.simulation import (
    OperationLogResponse,
    PlayLogResponse,
    _Report,
)


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
    simulation_container = character_provider.get_simulation_container(
        metadata.simulation_environment,
    )
    engine = simulation_container.operation_engine()

    for op_or_console in op_or_consoles:
        if is_console_command(op_or_console):
            _ = engine.console(cast(ConsoleText, op_or_console))
            continue

        engine.exec(cast(Operation, op_or_console))

    responses: list[OperationLogResponse] = []
    history = engine.history()
    damage_calculator = simulation_container.damage_calculator()

    for idx, operation_log in enumerate(history):
        playlog_responses = []

        for playlog in operation_log.playlogs:
            viewer = engine.get_viewer(playlog)
            entry = engine.get_simulation_entry(playlog)
            damage_logs: list[DamageLog] = entry.damage_logs

            damages = [
                (damage_log.name, damage_calculator.get_damage(damage_log))
                for damage_log in damage_logs
            ]
            damage = damage_calculator.calculate_damage(entry)

            playlog_responses.append(
                PlayLogResponse(
                    events=playlog.events,
                    validity_view={v.name: v for v in viewer("validity")},
                    running_view={v.name: v for v in viewer("running")},
                    buff_view=viewer("buff"),
                    clock=playlog.clock,
                    report=_Report(time_series=[entry]),
                    delay=playlog.get_delay_left(),
                    action=playlog.action,
                    checkpoint=playlog.checkpoint,
                    damage=damage,
                    damages=damages,
                )
            )

        responses.append(
            OperationLogResponse(
                index=idx,
                logs=playlog_responses,
                hash=operation_log.hash,
                previous_hash=operation_log.previous_hash,
                operation=operation_log.operation,
            )
        )

    return responses


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
