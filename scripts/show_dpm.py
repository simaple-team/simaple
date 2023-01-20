import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType
from simaple.simulate.actor import ActionRecorder
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
    actor = container.client_configuration().get_mdc_actor()

    environment = archmagefb_client.environment

    recorder = ActionRecorder("record.tsv")
    report = Report()
    archmagefb_client.add_handler(ReportEventHandler(report))

    events = []
    with recorder.start() as rec:
        while environment.show("clock") < 180_000:
            action = actor.decide(environment, events)
            events = archmagefb_client.play(action)
            rec.write(action, environment.show("clock"))

    print(
        f"{environment.show('clock')} | {container.dpm_calculator().calculate_dpm(report):,} "
    )


if __name__ == "__main__":
    test_actor()
