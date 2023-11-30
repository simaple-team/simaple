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


def test_actor():
    container = SimulationContainer()
    container.config.from_dict(setting.model_dump())

    report = Report()
    engine = container.operation_engine()
    engine.add_callback(ReportWriteCallback(report))

    policy = container.engine_configuration().get_default_policy()
    import time

    start = time.time()
    while engine.get_current_viewer()("clock") < 180_000:
        engine.exec_policy(policy, early_stop=180_000)

    end = time.time()

    print(
        f"{engine.get_current_viewer()('clock')} | {container.dpm_calculator().calculate_dpm(report):,} "
    )

    for operation_log in engine.operation_logs():
        timestamp = operation_log.playlogs[0].clock
        ops = operation_log.operation
        print(f"{timestamp:.3f} | {ops.expr}")


if __name__ == "__main__":
    test_actor()
