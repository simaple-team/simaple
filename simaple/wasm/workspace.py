from typing import cast

from simaple.container.plan_metadata import PlanMetadata
from simaple.container.simulation import SimulationContainer, SimulationEnvironment
from simaple.simulate.policy.base import ConsoleText, Operation, is_console_command
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.simulate.report.base import DamageLog
from simaple.wasm.base import (
    MaybePyodide,
    pyodide_reveal_dict,
    return_js_object_from_pydantic_list,
    return_js_object_from_pydantic_object,
)
from simaple.wasm.models.simulation import (
    OperationLogResponse,
    PlayLogResponse,
    _Report,
)


@return_js_object_from_pydantic_list
def run(
    plan: str,
    serialized_character_provider: MaybePyodide,
) -> list[OperationLogResponse]:
    _, op_or_consoles = parse_simaple_runtime(plan.strip())

    simulation_environment = SimulationEnvironment.model_validate(
        pyodide_reveal_dict(serialized_character_provider)
    )
    simulation_container = SimulationContainer(simulation_environment)
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


@return_js_object_from_pydantic_object
def getSerializedCharacterProvider(
    plan: str,
) -> SimulationEnvironment:
    metadata_dict, _ = parse_simaple_runtime(plan.strip())
    metadata = PlanMetadata.model_validate(metadata_dict)

    if metadata.provider is None:
        raise ValueError("Character provider is not provided")

    simulation_environment = metadata.provider.get_simulation_environment()

    return simulation_environment
