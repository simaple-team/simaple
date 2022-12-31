import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.core.jobtype import JobType
from simaple.data.damage_logic import get_damage_logic
from simaple.simulate.actor import ActionRecorder, DefaultMDCActor
from simaple.simulate.report.base import Report, ReportEventHandler
from simaple.simulate.report.dpm import DPMCalculator, LevelAdvantage


def test_actor(dualblade_client, character_stat):
    actor = DefaultMDCActor(
        order=[
            "히든 블레이드",
            "플래시 뱅",
            "파이널 컷",
            "써든레이드",
            "메이플 여신의 축복",
            "얼티밋 다크 사이트",
            "에픽 어드벤쳐",
            "레디 투 다이",
            "블레이드 토네이도",
            "카르마 퓨리",
            "블레이드 스톰",
            "아수라",
            "팬텀 블로우",
        ]
    )

    environment = dualblade_client.environment

    recorder = ActionRecorder("record.tsv")
    report = Report()
    dualblade_client.add_handler(ReportEventHandler(report))

    dpm_calculator = DPMCalculator(
        character_spec=character_stat,
        damage_logic=get_damage_logic(
            JobType.archmagefb, 0
        ),  # TODO: change JobType to dualblade
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
    )

    events = []
    with recorder.start() as rec:
        while environment.show("clock") < 50_000:
            action = actor.decide(dualblade_client.environment, events)
            events = dualblade_client.play(action)
            rec.write(action, environment.show("clock"))

    print(f"{environment.show('clock')} | {dpm_calculator.calculate_dpm(report):,} ")

    assert int(dpm_calculator.calculate_dpm(report)) == 2_709_138_952_046
