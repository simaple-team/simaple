import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.core.damage import INTBasedDamageLogic
from simaple.simulate.actor import ActionRecorder, DefaultMDCActor
from simaple.simulate.component.view import (
    BuffParentView,
    RunningParentView,
    ValidityParentView,
)
from simaple.simulate.report.base import Report, ReportEventHandler
from simaple.simulate.report.dpm import DPMCalculator, LevelAdvantage


def test_actor(adele_client, character_stat):
    actor = DefaultMDCActor(
        order=[
            "인피니트",
            "마커",
            "오더",
            "그레이브",
            "게더링",
            "블로섬",
            "디바이드",
        ]
    )
    events = []
    environment = adele_client.environment
    ValidityParentView.build_and_install(environment, "validity")
    BuffParentView.build_and_install(environment, "buff")
    RunningParentView.build_and_install(environment, "running")

    recorder = ActionRecorder("record.tsv")
    report = Report()

    adele_client.add_handler(ReportEventHandler(report))

    dpm_calculator = DPMCalculator(
        character_spec=character_stat,
        damage_logic=INTBasedDamageLogic(attack_range_constant=1.2, mastery=0.95),
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
    )

    events = []
    with recorder.start() as rec:
        while environment.show("clock") < 50_000:
            action = actor.decide(adele_client.environment, events)
            events = adele_client.play(action)
            rec.write(action, environment.show("clock"))

    print(f"{environment.show('clock')} | {dpm_calculator.calculate_dpm(report):,} ")
    assert int(dpm_calculator.calculate_dpm(report)) == 2_511_974_882_309
