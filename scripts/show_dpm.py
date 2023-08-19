import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core.job_category import JobCategory
from simaple.core.jobtype import JobType
from simaple.simulate.policy.base import OperationRecorder, get_interpreter
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

    recorder = OperationRecorder("record.tsv")
    report = Report()
    archmagefb_client.add_handler(ReportEventHandler(report))
    interpreter = get_interpreter(archmagefb_client)

    with recorder.start() as rec:
        while environment.show("clock") < 180_000:
            operand = policy.decide(environment)
            recorder.write(operand)
            interpreter.exec(operand)

    print(
        f"{environment.show('clock')} | {container.dpm_calculator().calculate_dpm(report):,} "
    )


if __name__ == "__main__":
    test_actor()
