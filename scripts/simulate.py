from enum import Enum

import fire

import simaple.simulate.component.common  # noqa: F401
from simaple.container.memoizer import PersistentStorageMemoizer
from simaple.container.plan_metadata import PlanMetadata
from simaple.container.simulation import SimulationContainer
from simaple.simulate.base import PlayLog
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.simulate.report.base import SimulationEntry
from simaple.simulate.report.feature import (
    DamageShareFeature,
    MaximumDealingIntervalFeature,
)


class PlayStatus(Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    PASSED = "PASSED"


def get_status_string(status: PlayStatus):
    if status == PlayStatus.PASSED:
        return "\033[41m[PASSED]\033[0m"
    elif status == PlayStatus.ACCEPT:
        return "\033[92m[ACCEPT]\033[0m"
    else:
        return "\033[91m[REJECT]\033[0m"


def show_damage_as_string(damage: float):
    if damage == 0:
        return ""
    elif damage < 1000:
        return f"{damage:03.2f}"
    elif damage < 1000000:
        return f"{damage/1000:03.2f}K"
    elif damage < 1000000000:
        return f"{damage/1000000:03.2f}M"
    else:
        return f"{damage/1000000000:03.2f}B"


def _get_status(playlog: PlayLog, entry: SimulationEntry) -> PlayStatus:
    if len(playlog.events) == 0:
        return PlayStatus.PASSED
    if entry.accepted:
        return PlayStatus.ACCEPT
    else:
        return PlayStatus.REJECT


def run(plan_file: str):
    with open(plan_file, "r") as f:
        plan_metadata_dict, commands = parse_simaple_runtime(f.read())

    _simulation_environment_memoizer = PersistentStorageMemoizer()

    plan_metadata = PlanMetadata.model_validate(plan_metadata_dict)
    environment = _simulation_environment_memoizer.compute_environment(
        plan_metadata.get_environment_provider_config()  # type: ignore
    )
    simulation_container = SimulationContainer(environment)

    engine = simulation_container.operation_engine()
    damage_calculator = simulation_container.damage_calculator()
    damage_share = DamageShareFeature(damage_calculator)

    for command in commands:
        operation_log = engine.exec(command)
        if operation_log.description:
            print(f"\033[90m[DEBUG_]{operation_log.description}\033[0m")

        for playlog in operation_log.playlogs:
            entry = engine.get_simulation_entry(playlog)
            damage_share.update(entry)
            total_damage = sum(
                [
                    damage_calculator.get_damage(damage_log)
                    for damage_log in entry.damage_logs
                ]
            )
            print(
                f"{get_status_string(_get_status(playlog, entry))}{entry.clock:6.0f}s | {show_damage_as_string(total_damage).rjust(8)} | {entry.action}|"
            )

    report = list(engine.simulation_entries())

    feature = MaximumDealingIntervalFeature(30000)
    damage_share.show()
    damage, _start, _end = feature.find_maximum_dealing_interval(
        report, damage_calculator
    )

    print(
        f"{engine.get_current_viewer()('clock')} | {damage:,} ( {damage / 1_000_000_000_000:.3f}조 ) / 30s - {simulation_container.environment.jobtype}"
    )


def run_from_cli():
    fire.Fire(run)


if __name__ == "__main__":
    fire.Fire(run)
