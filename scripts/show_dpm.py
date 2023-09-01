import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType
from simaple.simulate.policy import get_shell
from simaple.simulate.report.base import Report, ReportEventHandler

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
    container.config.from_pydantic(setting)

    archmagefb_client = container.client()
    policy = container.client_configuration().get_default_policy()

    environment = archmagefb_client.environment

    report = Report()
    archmagefb_client.add_handler(ReportEventHandler(report))
    shell = get_shell(archmagefb_client)

    while environment.show("clock") < 50_000:
        shell.exec_policy(policy, early_stop=50_000)

    print(
        f"{environment.show('clock')} | {container.dpm_calculator().calculate_dpm(report):,} "
    )


if __name__ == "__main__":
    test_actor()
