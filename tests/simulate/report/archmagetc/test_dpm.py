import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.core.jobtype import JobType
from simaple.data.damage_logic import get_damage_logic
from simaple.simulate.actor import ActionRecorder, DefaultMDCActor
from simaple.simulate.kms import get_client
from simaple.simulate.report.base import Report, ReportEventHandler
from simaple.simulate.report.dpm import DPMCalculator, LevelAdvantage


def test_actor(character_stat):
    archmagetc_client = get_client(
        ActionStat(),
        ["archmagetc", "common", "adventurer.magician"],
        {"character_level": 260},
        {},
        {},
    )

    actor = DefaultMDCActor(
        order=[
            "오버로드 마나",
            "엘퀴네스",
            "아이스 오라",
            "인피니티",
            "소울 컨트랙트",
            "메이플 여신의 축복",
            "에픽 어드벤처",
            "스피릿 오브 스노우",
            "아이스 에이지",
            "라이트닝 스피어",
            "블리자드",
            "주피터 썬더",
            "썬더 브레이크",
            "프로즌 오브",
            "체인 라이트닝",
        ]
    )

    environment = archmagetc_client.environment

    recorder = ActionRecorder("record.tsv")
    report = Report()

    archmagetc_client.add_handler(ReportEventHandler(report))

    dpm_calculator = DPMCalculator(
        character_spec=character_stat,
        damage_logic=get_damage_logic(JobType.archmagetc, 0),
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
    )

    events = []
    with recorder.start() as rec:
        while environment.show("clock") < 50_000:
            action = actor.decide(archmagetc_client.environment, events)
            events = archmagetc_client.play(action)
            rec.write(action, environment.show("clock"))

    print(f"{environment.show('clock')} | {dpm_calculator.calculate_dpm(report):,} ")

    assert int(dpm_calculator.calculate_dpm(report)) == 1_242_953_386_834
