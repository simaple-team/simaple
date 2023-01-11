import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.core.jobtype import JobType
from simaple.data.damage_logic import get_damage_logic
from simaple.simulate.actor import ActionRecorder, DefaultMDCActor
from simaple.simulate.report.base import Report, ReportEventHandler
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage


def test_actor(adele_client, character_stat):
    actor = DefaultMDCActor(
        order=[
            "매직 서킷 풀 드라이브",
            "그란디스 여신의 축복(레프)",
            "리스토어",
            "인피니트",
            "스톰",
            "마커",
            "오더",
            "그레이브",
            "테리토리",
            "루인",
            "게더링",
            "블로섬",
            "레조넌스",
            "샤드",
            "디바이드",
        ]
    )

    environment = adele_client.environment

    recorder = ActionRecorder("record.tsv")
    report = Report()
    adele_client.add_handler(ReportEventHandler(report))

    dpm_calculator = DamageCalculator(
        character_spec=character_stat,
        damage_logic=get_damage_logic(
            JobType.archmagefb, 0
        ),  # TODO: change JobType to adele
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

    assert int(dpm_calculator.calculate_dpm(report)) == 3_582_571_067_088
