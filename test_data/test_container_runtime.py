import os

from inline_snapshot import snapshot

from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.memoizer import PersistentStorageMemoizer
from simaple.container.simulation import get_damage_calculator
from simaple.container.usecase.builtin import get_engine
from simaple.core.jobtype import JobType
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.simulate.report.base import SimulationEntry


def container_test_setting(
    jobtype,
    options: dict = None,
):
    if options is None:
        options = {}

    return BaselineEnvironmentProvider(
        tier="Legendary",
        jobtype=jobtype,
        level=270,
        passive_skill_level=0,
        combat_orders_level=1,
        weapon_pure_attack_power=options.get("weapon_pure_attack_power", 0),
        artifact_level=40,
        hexa_mastery_level=1,
        v_skill_level=30,
        v_improvements_level=60,
        hexa_improvements_level=10,
        weapon_attack_power=options.get("weapon_attack_power", 0),
    )


def run_actor(environment_provider: BaselineEnvironmentProvider, jobtype: JobType):
    environment = PersistentStorageMemoizer(
        os.path.join(os.path.dirname(__file__), ".memo.simaple.json")
    ).compute_environment(environment_provider)

    engine = get_engine(environment)

    with open(
        os.path.join(
            os.path.dirname(__file__), "asset", f"{environment.jobtype.value}.simaple"
        ),
        "r",
    ) as f:
        _, commands = parse_simaple_runtime(f.read())

    for command in commands:
        engine.exec(command)

    report = list(engine.simulation_entries())

    """
    with open("operation.log", "w") as f:
        for op in engine.operation_logs():
            f.write(op.command.expr +'\n')

    with open("history.log", "w") as f:
        for op in engine.operation_logs():
            for playlog in op.playlogs:
                f.write(f"{playlog.clock} | {playlog.action} | {playlog.events} \n")
    """

    damage_calculator = get_damage_calculator(environment)

    def aggregate_by_skill(report: list[SimulationEntry]):
        skill_dpm = {}
        for entry in report:
            for log in entry.damage_logs:
                if log.name not in skill_dpm:
                    skill_dpm[log.name] = 0
                skill_dpm[log.name] += damage_calculator.get_damage(log)
        return skill_dpm

    result = aggregate_by_skill(report)
    dpm = damage_calculator.calculate_dpm(report)
    print(f"{engine.get_current_viewer()('clock')} | {jobtype} | {dpm:,} ")
    print(result)
    return result, dpm


def test_archmagefb_actor():
    # given
    environment_provider = container_test_setting(JobType.archmagefb)

    # when
    result, dpm = run_actor(environment_provider, JobType.archmagefb)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "이프리트 VI": 188242207479.8541,
                "인페르날 베놈": 2882201352316.544,
                "파이어 오라 VI": 311440135921.1418,
                "메테오 VI(패시브)": 672619013508.3517,
                "메테오 VI": 98079157281.17737,
                "이그나이트 VI": 925336568196.3773,
                "포이즌 리젼": 799229472260.6707,
                "포이즌 노바": 670890233773.3075,
                "도트 퍼니셔": 960425088338.1971,
                "메기도 플레임 VI": 268286698041.8797,
                "퓨리 오브 이프리트": 838927061359.0536,
                "미스트 이럽션 VI": 1564778990846.9922,
                "포이즌 체인": 567093827666.5518,
                "플레임 헤이즈 VI": 639702494996.9893,
                "포이즌 미스트": 91785046388.24673,
                "플레임 스윕 VI": 1556938946060.1423,
            },
            15509787381838.75,
        )
    )


def test_archmagetc_actor():
    # given
    environment_provider = container_test_setting(JobType.archmagetc)

    # when
    result, dpm = run_actor(environment_provider, JobType.archmagetc)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "프로즌 라이트닝": 2181975959355.241,
                "엘퀴네스": 102169613849.74362,
                "아이스 에이지": 373849418950.47473,
                "라이트닝 스피어": 767736740862.7377,
                "스피릿 오브 스노우": 1418991236574.3643,
                "블리자드 VI": 68008136712.755905,
                "주피터 썬더": 1423450883787.6738,
                "썬더 브레이크": 848918199296.8478,
                "프로즌 오브 VI": 563785102582.0892,
                "블리자드 VI(패시브)": 483626009960.599,
                "체인 라이트닝 VI": 2536352654423.466,
            },
            12812449680375.953,
        )
    )


def test_bishop_actor():
    # given
    environment_provider = container_test_setting(JobType.bishop)

    # when
    result, dpm = run_actor(environment_provider, JobType.bishop)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "엔젤릭 터치": 8953128434.082998,
                "제네시스": 97153284815.7926,
                "트라이엄프 페더 VI": 937021377602.358,
                "바하뮤트": 373763959390.8871,
                "헤븐즈 도어": 74882780167.66914,
                "파운틴 포 엔젤": 317342508564.4191,
                "피스메이커": 532923228823.2052,
                "디바인 퍼니시먼트": 1656197794094.8596,
                "엔젤 오브 리브라": 856634162025.8597,
                "엔젤레이 VI": 2972503595322.2104,
            },
            9374102777534.545,
        )
    )


def test_mechanic_actor():
    # given
    environment_provider = container_test_setting(JobType.mechanic)

    # when
    result, dpm = run_actor(environment_provider, JobType.mechanic)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "메카 캐리어": 4133960315812.8975,
                "호밍 미사일 VI": 6272530717706.716,
                "로봇 런처: RM7": 189761169598.24673,
                "마그네틱 필드": 226346884405.45798,
                "로봇 팩토리: RM1": 555178781979.1685,
                "메탈아머 전탄발사": 2947638655537.0415,
                "멀티플 옵션 : M-FL": 1432313954429.6052,
                "마이크로 미사일 컨테이너": 744059186522.6522,
                "디스토션 필드": 327063616936.7898,
                "그라운드 제로": 4452224774161.094,
                "레지스탕스 라인 인팬트리": 180965115715.05066,
                "매시브 파이어: IRON-B VI": 610625594189.9607,
                "매시브 파이어: IRON-B VI (폭발)": 142836571402.77872,
            },
            9069404098141.459,
        )
    )


def test_adele_actor():
    # given
    environment_provider = container_test_setting(
        JobType.adele,
        {
            "weapon_attack_power": 700,
            "weapon_pure_attack_power": 295,
        },
    )

    # when
    result, dpm = run_actor(environment_provider, JobType.adele)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "인피니트": 3387377893370.838,
                "마커": 159287272319.3397,
                "그레이브": 102023072549.63821,
                "테리토리": 658445257677.1439,
                "리스토어": 250676330707.76315,
                "루인": 473401549393.3876,
                "레조넌스": 2529577527507.6978,
            },
            9022421125925.799,
        )
    )


def test_windbreaker_actor():
    # given
    environment_provider = container_test_setting(
        JobType.windbreaker,
        {
            "weapon_attack_power": 789,
        },
    )

    # when
    result, dpm = run_actor(environment_provider, JobType.windbreaker)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "가이디드 애로우": 289261360364.29443,
                "핀포인트 피어스": 6518420074.618698,
                "스톰 브링어": 648511017573.6039,
                "스톰 윔": 600474634231.9185,
                "윈드 월": 1172926533817.5547,
                "하울링 게일": 3234934242190.596,
                "볼텍스 스피어": 853716275295.0952,
                "시그너스 팔랑크스": 467403659906.75977,
                "아이들 윔": 666388547906.0151,
                "천공의 노래 VI": 1335682963619.431,
            },
            11108763658658.555,
        )
    )


def test_soulmaster_actor():
    # given
    environment_provider = container_test_setting(
        JobType.soulmaster,
        {
            "weapon_attack_power": 789,
        },
    )

    # when
    result, dpm = run_actor(environment_provider, JobType.soulmaster)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "코스모스": 1058646457748.2843,
                "소울 이클립스": 1784959081333.1592,
                "크로스 더 스틱스": 4823730129507.715,
                "코스믹 버스트": 900609279382.5316,
                "플레어 슬래시": 289591623962.6182,
                "코스믹 샤워": 349553135154.1188,
                "엘리시온": 603336290733.7124,
                "솔라 슬래시/루나 디바이드": 751814516698.7421,
            },
            12626707130329.777,
        )
    )


def test_dualblade_actor():
    # given
    environment_provider = container_test_setting(
        JobType.dualblade,
        {
            "weapon_attack_power": 700,
        },
    )

    # when
    result, dpm = run_actor(environment_provider, JobType.dualblade)

    # then
    assert (result, dpm) == snapshot(
        (
            {
                "플래시 뱅": 1424858330.6067657,
                "히든 블레이드": 410808069553.06537,
                "파이널 컷": 3611230542.7850847,
                "써든레이드": 50071868343.58797,
                "블레이드 토네이도": 582750243145.4269,
                "카르마 퓨리": 671377719062.5751,
                "아수라 VI": 595361826614.028,
                "블레이드 스톰": 1158422114494.4902,
                "팬텀 블로우 VI": 1596122662785.745,
                "헌티드 엣지 - 나찰": 312663727279.5127,
            },
            6439817730989.216,
        )
    )
