import time
from cProfile import Profile

import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType
from simaple.simulate.report.base import Report, ReportWriteCallback

setting = SimulationSetting(
    tier="Legendary",
    jobtype=JobType.archmagefb,
    job_category=JobCategory.magician,
    level=270,
    passive_skill_level=0,
    combat_orders_level=1,
    v_skill_level=30,
    v_improvements_level=60,
)


container = SimulationContainer()
container.config.from_dict(setting.model_dump())

engine = container.operation_engine()
policy = container.engine_configuration().get_default_policy()

report = Report()
engine.add_callback(ReportWriteCallback(report))


def run():
    start = time.time()
    while engine.get_current_viewer()("clock") < 180_000:
        engine.exec_policy(policy, early_stop=180_000)

    print(
        f"{engine.get_current_viewer()('clock')} | {container.dpm_calculator().calculate_dpm(report):,} "
    )
    end = time.time()
    print(f"elapsed: {end - start}")

    # assert 8_264_622_367_162.877 == container.dpm_calculator().calculate_dpm(report)


if __name__ == "__main__":
    profiler = Profile()
    profiler.run("run()")

    profiler.dump_stats("test.prof")
