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


def test_actor(archmagetc_client, character_stat):
    actor = DefaultMDCActor(
        order=[
            "오버로드 마나",
            "엘퀴네스",
            "아이스 오라",
            "인피니티",
            "소울 컨트랙트",
            "메이플 여신의 축복",
            "메디테이션",
            "에픽 어드벤처",
            "아이스 에이지",
            "라이트닝 스피어",
            "블리자드",
            "썬더 브레이크",
            "프로즌 오브",
            "체인 라이트닝",
        ]
    )
    events = []
    environment = archmagetc_client.environment
    ValidityParentView.build_and_install(environment, "validity")
    BuffParentView.build_and_install(environment, "buff")
    RunningParentView.build_and_install(environment, "running")

    recorder = ActionRecorder("record.tsv")
    report = Report()

    archmagetc_client.add_handler(ReportEventHandler(report))

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
            action = actor.decide(archmagetc_client.environment, events)
            events = archmagetc_client.play(action)
            rec.write(action, environment.show("clock"))

    print(f"{environment.show('clock')} | {dpm_calculator.calculate_dpm(report):,} ")
    report.save("report.tsv")
