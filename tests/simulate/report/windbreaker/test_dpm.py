import simaple.simulate.component.skill  # pylint: disable=W0611
from simaple.core.jobtype import JobType
from simaple.data.damage_logic import get_damage_logic
from simaple.simulate.actor import ActionRecorder, DefaultMDCActor
from simaple.simulate.report.base import Report, ReportEventHandler
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage


def test_actor(windbreaker_get_client, windbreaker_stat):
    actor = DefaultMDCActor(
        order=[
            "엘리멘트 : 스톰",
            "트라이플링 윔",
            "가이디드 애로우",
            "시그너스 나이츠",
            "샤프 아이즈",
            "스톰 브링어",
            "초월자 시그너스의 축복",
            "윈드 월",
            "글로리 오브 가디언즈",
            "스톰 윔",
            "크리티컬 리인포스",
            "소울 컨트랙트",
            "핀포인트 피어스",
            "하울링 게일",
            "볼텍스 스피어",
            "시그너스 팔랑크스",
            "아이들 윔",
            "천공의 노래",
        ]
    )

    windbreaker_client = windbreaker_get_client(windbreaker_stat)

    environment = windbreaker_client.environment

    recorder = ActionRecorder("record.tsv")
    report = Report()
    windbreaker_client.add_handler(ReportEventHandler(report))

    dpm_calculator = DamageCalculator(
        character_spec=windbreaker_stat,
        damage_logic=get_damage_logic(JobType.windbreaker, 0),
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
    )

    events = []
    with recorder.start() as rec:
        while environment.show("clock") < 50_000:
            action = actor.decide(windbreaker_client.environment, events)
            events = windbreaker_client.play(action)
            rec.write(action, environment.show("clock"))

    print(f"{environment.show('clock')} | {dpm_calculator.calculate_dpm(report):,} ")

    assert int(dpm_calculator.calculate_dpm(report)) == 3_720_894_843_414
