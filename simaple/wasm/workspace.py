import json
from typing import cast

import pydantic
import yaml

from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.plan_metadata import PlanMetadata
from simaple.container.simulation import OperationEngine
from simaple.simulate.policy.base import ConsoleText, Operation, is_console_command
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.simulate.report.base import DamageLog
from simaple.simulate.report.dpm import DamageCalculator
from simaple.simulate.report.feature import MaximumDealingIntervalFeature
from simaple.wasm.base import (
    pyodide_reveal_base_model,
    return_js_object_from_pydantic_list,
    return_js_object_from_pydantic_object,
)
from simaple.wasm.examples import get_example_plan
from simaple.wasm.models.simulation import (
    DamageRecord,
    OperationLogResponse,
    PlayLogResponse,
    _Report,
)


def _extract_engine_history_as_response(
    engine: OperationEngine,
    damage_calculator: DamageCalculator,
) -> list[OperationLogResponse]:
    responses: list[OperationLogResponse] = []
    history = engine.history()

    for idx, operation_log in enumerate(history):
        playlog_responses = []

        for playlog in operation_log.playlogs:
            viewer = engine.get_viewer(playlog)
            entry = engine.get_simulation_entry(playlog)
            damage_logs: list[DamageLog] = entry.damage_logs

            damages = [
                DamageRecord(
                    name=damage_log.name,
                    damage=damage_calculator.get_damage(damage_log),
                    hit=damage_log.hit,
                )
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
                    total_damage=damage,
                    damage_records=damages,
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


@return_js_object_from_pydantic_list
def runPlan(
    plan: str,
) -> list[OperationLogResponse]:
    """
    plan을 받아서 environment 필드를 참조해 계산을 수행합니다. environment 필드가 비어있다면, 오류를 발생시킵니다.
    """
    plan_metadata_dict, op_or_consoles = parse_simaple_runtime(plan.strip())

    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)
    if plan_metadata.environment is None or plan_metadata.environment == {}:
        raise ValueError("Environment field is not provided")

    simulation_container = plan_metadata.load_container()
    engine = simulation_container.operation_engine()

    for op_or_console in op_or_consoles:
        if is_console_command(op_or_console):
            _ = engine.console(cast(ConsoleText, op_or_console))
            continue

        engine.exec(cast(Operation, op_or_console))

    return _extract_engine_history_as_response(
        engine, simulation_container.damage_calculator()
    )


def hasEnvironment(plan: str) -> bool:
    """plan이 environment 필드를 가지고 있는지 확인합니다."""
    plan_metadata_dict, _ = parse_simaple_runtime(plan.strip())
    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)

    return plan_metadata.environment is not None and plan_metadata.environment != {}


def provideEnvironmentAugmentedPlan(plan: str) -> str:
    """plan을 받아서 environment 필드를 새로 쓴 plan을 반환합니다."""
    metadata_dict, _ = parse_simaple_runtime(plan.strip())
    metadata = PlanMetadata.model_validate(metadata_dict)

    if metadata.provider is None:
        raise ValueError("Character provider is not provided")

    simulation_environment = metadata.provider.get_simulation_environment()
    metadata.environment = simulation_environment
    _, original_operations = plan.split("\n---")[0], "\n---".join(
        plan.split("\n---")[1:]
    )

    augmented_metadata = yaml.safe_dump(
        json.loads(metadata.model_dump_json()), indent=2
    )
    return f"---\n{augmented_metadata}\n---\n{original_operations}"


class MaximumDealingIntervalResult(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    damage: float
    start: int
    end: int


@return_js_object_from_pydantic_object
def computeMaximumDealingInterval(
    plan: str,
    interval: int,
) -> MaximumDealingIntervalResult:
    """
    interval as ms.
    """
    plan_metadata_dict, op_or_consoles = parse_simaple_runtime(plan.strip())

    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)
    if plan_metadata.environment is None or plan_metadata.environment == {}:
        raise ValueError("Environment field is not provided")

    simulation_container = plan_metadata.load_container()
    engine = simulation_container.operation_engine()

    for op_or_console in op_or_consoles:
        if is_console_command(op_or_console):
            _ = engine.console(cast(ConsoleText, op_or_console))
            continue

        engine.exec(cast(Operation, op_or_console))

    report = list(engine.simulation_entries())

    damage, _start, _end = MaximumDealingIntervalFeature(
        interval=interval
    ).find_maximum_dealing_interval(report, simulation_container.damage_calculator())
    return MaximumDealingIntervalResult(damage=damage, start=_start, end=_end)


def getInitialPlanFromBaselineEnvironment(
    environment_provider: BaselineEnvironmentProvider,
) -> str:
    """
    baseline environment을 받아서 plan을 생성합니다.
    """
    environment_provider = pyodide_reveal_base_model(
        environment_provider, BaselineEnvironmentProvider
    )
    base_plan = get_example_plan(environment_provider.jobtype)
    metadata_dict, _ = parse_simaple_runtime(base_plan.strip())

    metadata_dict["provider"] = {
        "name": environment_provider.get_name(),
        "data": environment_provider.model_dump(),
    }
    metadata = PlanMetadata.model_validate(metadata_dict)

    simulation_environment = environment_provider.get_simulation_environment()
    metadata.environment = simulation_environment

    _, original_operations = base_plan.split("\n---")[0], "\n---".join(
        base_plan.split("\n---")[1:]
    )

    augmented_metadata = yaml.safe_dump(
        json.loads(metadata.model_dump_json()), indent=2
    )
    return f"---\n{augmented_metadata}\n---\n{original_operations}"
