import simaple.simulate.component.skill  # noqa: F401
from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType
from simaple.simulate.strategy.base import exec_by_strategy

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

    engine = container.operation_engine()

    policy = container.skill_profile().get_default_policy()

    while engine.get_current_viewer()("clock") < 180_000:
        exec_by_strategy(engine, policy, early_stop=180_000)

    report = engine.create_full_report()

    for operation_log in engine.operation_logs():
        timestamp = operation_log.playlogs[0].clock
        ops = operation_log.operation
        print(f"{timestamp:.3f} | {ops.expr}")

    print(
        f"{engine.get_current_viewer()('clock')} | {container.dpm_calculator().calculate_dpm(report):,} "
    )


if __name__ == "__main__":
    test_actor()
