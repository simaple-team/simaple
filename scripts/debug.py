import simaple.simulate.component.skill  # noqa: F401
from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType
from simaple.simulate.report.base import Report
from simaple.simulate.report.feature import MaximumDealingIntervalFeature


def get_status_string(status: bool):
    if status:
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


class DebugInterface:
    def __init__(self) -> None:
        self._setting = SimulationSetting(
            tier="Legendary",
            jobtype=JobType.archmagefb,
            job_category=JobCategory.magician,
            level=270,
            passive_skill_level=0,
            combat_orders_level=1,
            v_skill_level=30,
            v_improvements_level=60,
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
            plan = f.read().splitlines()

        engine = self.get_engine()

        damage_calculator = self.get_dpm_calculator()

        plan_writer = _TimestampedPlanWriter()

        for command in plan:
            plan_writer.write(command, engine.get_current_viewer()("clock"))

            count = engine.exec_dsl(command, debug=True)
            for idx in range(-count, 0):
                op_log = engine.history().get(idx)
                report = Report()
                for playlog in op_log.playlogs:
                    entry = engine.get_simulation_entry(playlog)

                    total_damage = sum(
                        [
                            damage_calculator.get_damage(damage_log)
                            for damage_log in entry.damage_logs
                        ]
                    )

                    print(
                        f"{get_status_string(entry.accepted)}{entry.clock:6.0f}s | {show_damage_as_string(total_damage).rjust(8)} | {entry.action}|"
                    )

        report = engine.create_full_report()

        feature = MaximumDealingIntervalFeature(30000)
        feature.find_maximum_dealing_interval(report, damage_calculator)

        print(
            f"{engine.get_current_viewer()('clock')} | {self.get_dpm_calculator().calculate_total_damage(report):,} "
        )
        plan_writer.dump(plan_file.replace(".log", ".result.log"))


if __name__ == "__main__":
    debugger = DebugInterface()
    debugger.run("control.plan.log")
