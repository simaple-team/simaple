import os

from inline_snapshot import snapshot

import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.memoizer import PersistentStorageMemoizer
from simaple.container.simulation import get_damage_calculator, get_operation_engine
from simaple.core.jobtype import JobType
from simaple.data.jobs.builtin import get_builtin_strategy
from simaple.simulate.strategy.base import exec_by_strategy


def container_test_setting(
    jobtype,
    options: dict = None,
):
    if options is None:
        options = {}

    return BaselineEnvironmentProvider(
        tier="Legendary",
        jobtype=jobtype,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        weapon_pure_attack_power=options.get("weapon_pure_attack_power", 0),
        artifact_level=40,
        hexa_mastery_level=1,
        v_skill_level=30,
        v_improvements_level=60,
        hexa_improvements_level=10,
        weapon_attack_power=options.get("weapon_attack_power", 0),
    )


def run_actor(environment_provider: BaselineEnvironmentProvider, jobtype: JobType):
    environment = PersistentStorageMemoizer(
        os.path.join(os.path.dirname(__file__), ".memo.simaple.json")
    ).compute_environment(environment_provider)
    engine = get_operation_engine(environment)

    policy = get_builtin_strategy(environment.jobtype).get_priority_based_policy()

    while engine.get_current_viewer()("clock") < 50_000:
        exec_by_strategy(engine, policy)

    report = list(engine.simulation_entries())

    """
    with open("operation.log", "w") as f:
        for op in engine.operation_logs():
            f.write(op.operation.expr+'\n')

    with open("history.log", "w") as f:
        for op in engine.operation_logs():
            for playlog in op.playlogs:
                f.write(f"{playlog.clock} | {playlog.action} | {playlog.events} \n")
    """

    dpm = get_damage_calculator(environment).calculate_dpm(report)
    print(f"{engine.get_current_viewer()('clock')} | {jobtype} | {dpm:,} ")
    return dpm


def test_archmagefb_actor():
    # given
    environment_provider = container_test_setting(JobType.archmagefb)

    # when
    dpm = run_actor(environment_provider, JobType.archmagefb)

    # then
    assert int(dpm) == snapshot(16195121054262)


def test_archmagetc_actor():
    # given
    environment_provider = container_test_setting(JobType.archmagetc)

    # when
    dpm = run_actor(environment_provider, JobType.archmagetc)

    # then
    assert int(dpm) == snapshot(13407067282228)


def test_bishop_actor():
    # given
    environment_provider = container_test_setting(JobType.bishop)

    # when
    dpm = run_actor(environment_provider, JobType.bishop)

    # then
    assert int(dpm) == snapshot(9374188673726)


def test_mechanic_actor():
    # given
    environment_provider = container_test_setting(JobType.mechanic)

    # when
    dpm = run_actor(environment_provider, JobType.mechanic)

    # then
    assert int(dpm) == snapshot(7981609050409)


def test_adele_actor():
    # given
    environment_provider = container_test_setting(
        JobType.adele,
        {
            "weapon_attack_power": 700,
            "weapon_pure_attack_power": 295,
        },
    )

    # when
    dpm = run_actor(environment_provider, JobType.adele)

    # then
    assert int(dpm) == snapshot(9068638620941)


def test_windbreaker_actor():
    # given
    environment_provider = container_test_setting(
        JobType.windbreaker,
        {
            "weapon_attack_power": 789,
        },
    )

    # when
    dpm = run_actor(environment_provider, JobType.windbreaker)

    # then
    assert int(dpm) == snapshot(11178296867273)


def test_soulmaster_actor():
    # given
    environment_provider = container_test_setting(
        JobType.soulmaster,
        {
            "weapon_attack_power": 789,
        },
    )

    # when
    dpm = run_actor(environment_provider, JobType.soulmaster)

    # then
    assert int(dpm) == snapshot(12689549643945)


def test_dualblade_actor():
    # given
    environment_provider = container_test_setting(
        JobType.dualblade,
        {
            "weapon_attack_power": 700,
        },
    )

    # when
    dpm = run_actor(environment_provider, JobType.dualblade)

    # then
    assert int(dpm) == snapshot(6439866356676)
