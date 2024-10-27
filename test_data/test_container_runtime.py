import os

from inline_snapshot import snapshot

import simaple.simulate.component.common  # pylint: disable=W0611
from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.memoizer import PersistentStorageMemoizer
from simaple.container.simulation import get_damage_calculator, get_operation_engine
from simaple.core.jobtype import JobType
from simaple.data.jobs.builtin import get_builtin_strategy
from simaple.simulate.report.base import SimulationEntry
from simaple.simulate.strategy.base import exec_by_strategy


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
    engine = get_operation_engine(environment)

    policy = get_builtin_strategy(environment.jobtype).get_priority_based_policy()

    while engine.get_current_viewer()("clock") < 50_000:
        exec_by_strategy(engine, policy)

    report = list(engine.simulation_entries())

    """
    with open("operation.log", "w") as f:
        for op in engine.operation_logs():
            f.write(op.operation.expr+'\n')

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
                "이프리트": 167547809987.19308,
                "인페르날 베놈": 4582218084922.721,
                "파이어 오라": 277851198444.99695,
                "메테오(패시브)": 578583999008.295,
                "이그나이트": 811170543952.9205,
                "메테오": 88473033889.00569,
                "포이즌 노바": 676940185483.11,
                "도트 퍼니셔": 969138856781.5854,
                "메기도 플레임": 241107758217.2725,
                "퓨리 오브 이프리트": 846449583619.0264,
                "미스트 이럽션 VI": 1574286198865.0588,
                "포이즌 체인": 572250260556.3868,
                "플레임 헤이즈 VI": 644890288172.1376,
                "포이즌 미스트": 92621132645.42265,
                "플레임 스윕 VI": 1569507171569.5815,
            },
            16291536116733.748,
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
                "프로즌 라이트닝": 2201541377138.786,
                "엘퀴네스": 103001026130.62799,
                "아이스 에이지": 377201664899.1714,
                "라이트닝 스피어": 773888918603.4397,
                "스피릿 오브 스노우": 1431758862076.9639,
                "블리자드 VI": 68553112773.691414,
                "주피터 썬더": 1436006062897.8757,
                "썬더 브레이크": 856358540314.9589,
                "프로즌 오브 VI": 568392590011.8038,
                "블리자드 VI(패시브)": 487576570508.5926,
                "체인 라이트닝 VI": 2556229524315.2256,
            },
            12921485127508.79,
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
                "엔젤릭 터치": 9089605129.389559,
                "제네시스": 98694528069.31418,
                "트라이엄프 페더 VI": 951701381706.27,
                "바하뮤트": 379610521473.34076,
                "헤븐즈 도어": 76051471784.35988,
                "파운틴 포 엔젤": 322311582420.65466,
                "피스메이커": 540905517822.03564,
                "디바인 퍼니시먼트": 1680604051080.1382,
                "엔젤 오브 리브라": 869433330034.7766,
                "엔젤레이 VI": 3019270977935.103,
            },
            9518171218509.441,
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
                "메카 캐리어": 2352608222783.9346,
                "로봇 런처: RM7": 103007303509.85805,
                "마그네틱 필드": 120491046753.91942,
                "로봇 팩토리: RM1": 293234897173.6744, "멀티플 옵션 : M-FL": 752714065726.3594, "메탈아머 전탄발사": 1588720445348.7322,
                "마이크로 미사일 컨테이너": 1220290481679.8428,
                "디스토션 필드": 266098561331.82068,
                "레지스탕스 라인 인팬트리": 196046032742.0047,
            },
            8077981707480.637,
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
                "인피니트": 3422885315685.9727,
                "마커": 161012833495.5797,
                "그레이브": 103028207793.87389,
                "테리토리": 664803139213.5039,
                "리스토어": 253296350304.05316,
                "루인": 478362434182.9944,
                "레조넌스": 2553977574532.149,
            },
            9113801736525.219,
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
                "가이디드 애로우": 292002528495.4985,
                "핀포인트 피어스": 6591003098.961559,
                "스톰 브링어": 655673913716.9945,
                "스톰 윔": 607073620287.7146,
                "윈드 월": 1183982132525.0479,
                "하울링 게일": 3265041555139.396,
                "볼텍스 스피어": 861544638253.833,
                "시그너스 팔랑크스": 471626745347.9877,
                "아이들 윔": 672542739067.0979,
                "천공의 노래 VI": 1350543790751.3618,
            },
            11217512175669.35,
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
                "코스모스": 1072619783428.2711,
                "소울 이클립스": 1808519179594.8274,
                "크로스 더 스틱스": 4887399687553.882,
                "코스믹 버스트": 912496634862.8466,
                "플레어 슬래시": 293414012491.11017,
                "코스믹 샤워": 354166969890.1811,
                "엘리시온": 611299869531.2163,
                "솔라 슬래시/루나 디바이드": 761737894816.0385,
            },
            12793370032478.62,
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
                "플래시 뱅": 1667581884.7283971,
                "히든 블레이드": 480753090930.6608,
                "파이널 컷": 4225958309.8493214,
                "써든레이드": 58596522533.43942,
                "블레이드 토네이도": 681970677549.0599,
                "카르마 퓨리": 785688077089.6328,
                "아수라 VI": 696729539041.1208,
                "블레이드 스톰": 1355657802981.768,
                "팬텀 블로우 VI": 1867002159403.1157,
                "헌티드 엣지 - 나찰": 365898592829.2649,
            },
            7535222336055.003,
        )
    )