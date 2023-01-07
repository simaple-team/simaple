import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.core.damage import STRBasedDamageLogic
from simaple.simulate.actor import ActionRecorder, DefaultMDCActor
from simaple.simulate.component.view import (
    BuffParentView,
    RunningParentView,
    ValidityParentView,
)
from simaple.simulate.report.base import Report, ReportEventHandler
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage


def test_actor(soulmaster_client, soulmaster_stat):
    actor = DefaultMDCActor(
        order=[
            "솔루나 타임",
            "엘리멘트: 소울",
            "트루 사이트",
            "코스믹 버스트",
            "코스믹 샤워",
            "엘리시온",
            "크로스 더 스틱스",
            "솔라 슬래시/루나 디바이드",
        ]
    )
    events = []
    environment = soulmaster_client.environment
    ValidityParentView.build_and_install(environment, "validity")
    BuffParentView.build_and_install(environment, "buff")
    RunningParentView.build_and_install(environment, "running")

    recorder = ActionRecorder("record.tsv")
    report = Report()

    soulmaster_client.add_handler(ReportEventHandler(report))

    dpm_calculator = DamageCalculator(
        character_spec=soulmaster_stat,
        damage_logic=STRBasedDamageLogic(attack_range_constant=1.34, mastery=0.90),
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
    )

    events = []
    with recorder.start() as rec:
        while environment.show("clock") < 50_000:
            action = actor.decide(soulmaster_client.environment, events)
            events = soulmaster_client.play(action)
            rec.write(action, environment.show("clock"))

    report.save("report.tsv")

    print(f"{environment.show('clock')} | {dpm_calculator.calculate_dpm(report):,} ")
