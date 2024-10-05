import json

import pydantic
import yaml

from simaple.api.examples import get_example_plan
from simaple.api.models.simulation import (
    DamageRecord,
    OperationLogResponse,
    PlayLogResponse,
    _Report,
)
from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.plan_metadata import PlanMetadata
from simaple.container.simulation import (
    get_damage_calculator,
    get_operation_engine,
    get_skill_components,
)
from simaple.simulate.component.base import Component
from simaple.simulate.engine import OperationEngine
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.simulate.report.base import DamageLog
from simaple.simulate.report.dpm import DamageCalculator
from simaple.simulate.report.feature import MaximumDealingIntervalFeature


def _extract_engine_history_as_response(
    engine: OperationEngine,
    damage_calculator: DamageCalculator,
    start: int = 0,
    checkpoint_interval: int = 10,
) -> list[OperationLogResponse]:
    responses: list[OperationLogResponse] = []

    for idx, operation_log in enumerate(engine.operation_logs()):
        if idx < start:
            continue

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

            # Saves checkpoint iff it is a multiple of checkpoint_interval
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
                    checkpoint=(
                        playlog.checkpoint if idx % checkpoint_interval == 0 else None
                    ),
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
                command=operation_log.command,
                description=operation_log.description,
            )
        )

    return responses


def run_plan(
    plan: str,
) -> list[OperationLogResponse]:
    """
    plan을 받아서 environment 필드를 참조해 계산을 수행합니다. environment 필드가 비어있다면, 오류를 발생시킵니다.
    """
    plan_metadata_dict, commands = parse_simaple_runtime(plan.strip())

    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)
    if plan_metadata.environment is None or plan_metadata.environment == {}:
        raise ValueError("Environment field is not provided")

    environment = plan_metadata.get_environment()
    engine = get_operation_engine(environment)

    for command in commands:
        engine.exec(command)

    return _extract_engine_history_as_response(
        engine, get_damage_calculator(environment)
    )


def has_environment(plan: str) -> bool:
    """plan이 environment 필드를 가지고 있는지 확인합니다."""
    plan_metadata_dict, _ = parse_simaple_runtime(plan.strip())
    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)

    return plan_metadata.environment is not None and plan_metadata.environment != {}


def provide_environment_augmented_plan(plan: str) -> str:
    """plan을 받아서 environment 필드를 새로 쓴 plan을 반환합니다."""
    metadata_dict, _ = parse_simaple_runtime(plan.strip())
    metadata = PlanMetadata.model_validate(metadata_dict)

    if metadata.provider is None:
        raise ValueError("Character provider is not provided")

    simulation_environment = metadata.provider.get_simulation_environment()
    metadata.environment = simulation_environment
    _, original_operations = (
        plan.split("\n---")[0],
        "\n---".join(plan.split("\n---")[1:]),
    )

    augmented_metadata = yaml.safe_dump(
        json.loads(metadata.model_dump_json()),
        indent=2,
        allow_unicode=True,
    )
    return f"---\n{augmented_metadata}\n---\n{original_operations}"


class MaximumDealingIntervalResult(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    damage: float
    start: int
    end: int


def compute_maximum_dealing_interval(
    plan: str,
    interval: int,
) -> MaximumDealingIntervalResult:
    """
    interval as ms.
    """
    plan_metadata_dict, commands = parse_simaple_runtime(plan.strip())

    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)
    if plan_metadata.environment is None or plan_metadata.environment == {}:
        raise ValueError("Environment field is not provided")

    environment = plan_metadata.get_environment()
    engine = get_operation_engine(environment)

    for command in commands:
        engine.exec(command)

    report = list(engine.simulation_entries())

    damage, _start, _end = MaximumDealingIntervalFeature(
        interval=interval
    ).find_maximum_dealing_interval(report, get_damage_calculator(environment))
    return MaximumDealingIntervalResult(damage=damage, start=_start, end=_end)


def get_initial_plan_from_baseline(
    environment_provider: BaselineEnvironmentProvider,
) -> str:
    """
    baseline environment provider를 받아서 example plan을 생성합니다.
    """
    base_plan = get_example_plan(environment_provider.jobtype)
    metadata_dict, _ = parse_simaple_runtime(base_plan.strip())

    metadata_dict["provider"] = {
        "name": environment_provider.get_name(),
        "data": environment_provider.model_dump(),
    }
    metadata = PlanMetadata.model_validate(metadata_dict)

    _, original_operations = (
        base_plan.split("\n---")[0],
        "\n---".join(base_plan.split("\n---")[1:]),
    )

    augmented_metadata = yaml.safe_dump(
        json.loads(metadata.model_dump_json()), indent=2, allow_unicode=True
    )
    return f"---\n{augmented_metadata}\n---\n{original_operations}"


def run_plan_with_hint(
    previous_plan: str, previous_history: list[OperationLogResponse], plan: str
) -> list[OperationLogResponse]:
    previous_plan_metadata_dict, previous_commands = parse_simaple_runtime(
        previous_plan.strip()
    )
    plan_metadata_dict, commands = parse_simaple_runtime(plan.strip())
    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)

    environment = plan_metadata.get_environment()
    engine = get_operation_engine(environment)

    if plan_metadata_dict != previous_plan_metadata_dict:
        for command in commands:
            engine.exec(command)

        return _extract_engine_history_as_response(
            engine, get_damage_calculator(environment)
        )

    # Since first operation in history is always "init", we skip this for retrieval;
    history_for_matching = previous_history[1:]

    cache_count: int = 0

    for idx, command in enumerate(commands):
        if len(previous_commands) <= idx or len(history_for_matching) <= idx:
            break

        previous_command = previous_commands[idx]
        previous_operation_log = history_for_matching[idx]
        if previous_command != previous_operation_log.command:
            break

        if command == previous_command:
            cache_count += 1
            continue
        break

    # Find latest restorable operation log
    while cache_count > 0 and not previous_history[cache_count].contains_chekcpoint():
        cache_count -= 1

    engine.reload(
        [
            operation_log_response.restore_operation_log()
            for operation_log_response in previous_history[: cache_count + 1]
        ]
    )

    for command in commands[cache_count:]:
        engine.exec(command)

    new_operation_logs = _extract_engine_history_as_response(
        engine,
        get_damage_calculator(environment),
        start=cache_count + 1,
    )

    return previous_history[: cache_count + 1] + new_operation_logs


def get_all_component(
    plan: str,
) -> list[Component]:
    plan_metadata_dict, _ = parse_simaple_runtime(plan.strip())

    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)
    if plan_metadata.environment is None or plan_metadata.environment == {}:
        raise ValueError("Environment field is not provided")

    environment = plan_metadata.get_environment()
    skills = get_skill_components(environment)

    return skills
