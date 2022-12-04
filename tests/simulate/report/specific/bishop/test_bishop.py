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


def test_actor(bishop_client, character_stat):
    actor = DefaultMDCActor(
        order=[
            "오버로드 마나",
            "바하뮤트",
            "트라이엄프 페더",
            "인피니티",
            "소울 컨트랙트",
            "메이플 여신의 축복",
            "에픽 어드벤처",
            "제네시스",
            "파운틴 포 엔젤",
            "엔젤레이",
        ]
    )
    events = []
    environment = bishop_client.environment
    ValidityParentView.build_and_install(environment, "validity")
    BuffParentView.build_and_install(environment, "buff")
    RunningParentView.build_and_install(environment, "running")

    recorder = ActionRecorder("record.tsv")
    report = Report()

    bishop_client.add_handler(ReportEventHandler(report))

    dpm_calculator = DPMCalculator(
        character_spec=character_stat,
        damage_logic=INTBasedDamageLogic(attack_range_constant=1.2, mastery=0.95),
        armor=300,
        level=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
    )

    events = []
    with recorder.start() as rec:
        while environment.show("clock") < 50_000:
            action = actor.decide(bishop_client.environment, events)
            events = bishop_client.play(action)
            rec.write(action, environment.show("clock"))

    print(f"{environment.show('clock')} | {dpm_calculator.calculate_dpm(report):,} ")
    report.save("report.tsv")
