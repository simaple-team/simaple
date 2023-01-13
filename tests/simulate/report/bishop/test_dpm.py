import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.core.base import ActionStat
from simaple.core.jobtype import JobType
from simaple.data.damage_logic import get_damage_logic
from simaple.simulate.actor import ActionRecorder, DefaultMDCActor
from simaple.simulate.kms import get_client
from simaple.simulate.report.base import Report, ReportEventHandler
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage


def test_actor(character_stat):
    bishop_client = get_client(
        ActionStat(),
        ["bishop", "common", "adventurer.magician"],
        {
            "character_level": 260,
            "character_stat": character_stat,
        },
        {},
        {},
    )

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
            "헤븐즈 도어",
            "프레이",
            "엔젤 오브 리브라",
            "홀리 블러드",
            "피스메이커",
            "디바인 퍼니시먼트",
            "엔젤레이",
        ]
    )

    environment = bishop_client.environment

    recorder = ActionRecorder("record.tsv")
    report = Report()
    bishop_client.add_handler(ReportEventHandler(report))

    dpm_calculator = DamageCalculator(
        character_spec=character_stat,
        damage_logic=get_damage_logic(JobType.bishop, 0),
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
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

    assert int(dpm_calculator.calculate_dpm(report)) == 1_193_594_063_632
