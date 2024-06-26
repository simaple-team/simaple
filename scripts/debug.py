from enum import Enum

import fire

import simaple.simulate.component.skill  # noqa: F401
from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core.jobtype import JobType, get_job_category
from simaple.simulate.policy.parser import (
    is_console_command,
    parse_dsl_to_operations_or_console,
)
from simaple.simulate.report.base import PlayLog, SimulationEntry
from simaple.simulate.report.feature import MaximumDealingIntervalFeature


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


class _TimestampedPlanWriter:
    def __init__(self) -> None:
        self._commands = []

    def write(self, command: str, timestamp: float):
        self._commands.append(f"{command: <25} # {int(timestamp):,}ms")

    def dump(self, file_name: str):
        with open(file_name, "w") as f:
            f.write("\n".join(self._commands))


def _get_status(playlog: PlayLog, entry: SimulationEntry) -> PlayStatus:
    if len(playlog.events) == 0:
        return PlayStatus.PASSED
    if entry.accepted:
        return PlayStatus.ACCEPT
    else:
        return PlayStatus.REJECT


class DebugInterface:
    def __init__(self, jobtype: JobType | str) -> None:
        if isinstance(jobtype, str):
            jobtype = JobType(jobtype)

        self._setting = SimulationSetting(
            tier="Legendary",
            jobtype=jobtype,
            job_category=get_job_category(jobtype),
            level=270,
            passive_skill_level=0,
            combat_orders_level=1,
            v_skill_level=30,
            v_improvements_level=60,
            hexa_improvements_level=10,
            artifact_level=40,
        )

    def get_engine(self):
        container = SimulationContainer()
        container.config.from_dict(self._setting.model_dump())

        engine = container.operation_engine()

        return engine

    def get_dpm_calculator(self):
        container = SimulationContainer()
        container.config.from_dict(self._setting.model_dump())
        return container.dpm_calculator()

    def run(self, plan_file: str):
        with open(plan_file, "r") as f:
            plan = filter(
                lambda x: x and (not x.startswith("#")), f.read().splitlines()
            )

        engine = self.get_engine()

        damage_calculator = self.get_dpm_calculator()

        plan_writer = _TimestampedPlanWriter()

        for line in plan:
            plan_writer.write(line, engine.get_current_viewer()("clock"))

            operation_or_consoles = parse_dsl_to_operations_or_console(line)
            for op_or_console in operation_or_consoles:

                if is_console_command(op_or_console):
                    console_output = engine.console(op_or_console.text)
                    print(f"\033[90m[DEBUG_]{console_output}\033[0m")
                else:
                    op_log = engine.exec(op_or_console)
                    for playlog in op_log.playlogs:
                        entry = engine.get_simulation_entry(playlog)
                        total_damage = sum(
                            [
                                damage_calculator.get_damage(damage_log)
                                for damage_log in entry.damage_logs
                            ]
                        )
                        print(
                            f"{get_status_string(_get_status(playlog, entry))}{entry.clock:6.0f}s | {show_damage_as_string(total_damage).rjust(8)} | {entry.action}|"
                        )

        report = engine.create_full_report()

        feature = MaximumDealingIntervalFeature(30000)
        print(feature.find_maximum_dealing_interval(report, damage_calculator))

        print(
            f"{engine.get_current_viewer()('clock')} | {self.get_dpm_calculator().calculate_total_damage(report):,} "
        )
        plan_writer.dump(plan_file.replace(".simaple", ".result.simaple"))


if __name__ == "__main__":
    fire.Fire(DebugInterface)
