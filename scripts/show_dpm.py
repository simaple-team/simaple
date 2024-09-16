import simaple.simulate.component.skill  # noqa: F401
from simaple.container.cache import PersistentStorageCache
from simaple.container.character_provider import BaselineSimulationConfig
from simaple.container.simulation import SimulationSetting
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType
from simaple.simulate.strategy.base import exec_by_strategy

character_provider = BaselineSimulationConfig(
    tier="Legendary",
    jobtype=JobType.archmagefb,
    job_category=JobCategory.magician,
    level=270,
    passive_skill_level=0,
    combat_orders_level=1,
    artifact_level=40,
)

setting = SimulationSetting(
    v_skill_level=30,
    v_improvements_level=60,
)


def test_actor():
    container = PersistentStorageCache().get_simulation_container(
        setting, character_provider
    )

    engine = container.operation_engine()

    policy = container.skill_profile().get_default_policy()

    while engine.get_current_viewer()("clock") < 180_000:
        exec_by_strategy(engine, policy, early_stop=180_000)

    for operation_log in engine.operation_logs():
        timestamp = operation_log.playlogs[0].clock
        ops = operation_log.operation
        print(f"{timestamp:.3f} | {ops.expr}")

    print(
        f"{engine.get_current_viewer()('clock')} | {container.dpm_calculator().calculate_dpm(list(engine.simulation_entries())):,} "
    )


if __name__ == "__main__":
    test_actor()
