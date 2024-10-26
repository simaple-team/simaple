from simaple.container.simulation import SimulationEnvironment
from simaple.container.usecase.base import Usecase
from simaple.container.usecase.builtin.util import get_component_loader


def mechanic_usecase(environment: SimulationEnvironment) -> Usecase:

    mechanic_component = get_component_loader(environment)
    usecase = Usecase()

    usecase.use_component(mechanic_component("로디드 다이스"))
    usecase.use_component(mechanic_component("메탈아머: 탱크"))
    usecase.use_component(mechanic_component("로봇 마스터리"))
    usecase.use_component(mechanic_component("오픈 게이트: GX-9"))
    usecase.use_component(mechanic_component("서포트 웨이버: H-EX"))
    usecase.use_component(mechanic_component("로봇 런처: RM7"))
    usecase.use_component(mechanic_component("마그네틱 필드"))
    usecase.use_component(mechanic_component("로봇 팩토리: RM1"))
    usecase.use_component(mechanic_component("봄버 타임"))
    usecase.use_component(mechanic_component("디스토션 필드"))
    usecase.use_component(mechanic_component("멀티플 옵션: M-FL"))
    usecase.use_component(mechanic_component("마이크로 미사일 컨테이너"))
    usecase.use_component(mechanic_component("메탈아머 전탄발사"))
    usecase.use_component(mechanic_component("메카 캐리어"))

    usecase.use_component(mechanic_component("매시브 파이어: IRON-B VI"))
    usecase.use_component(mechanic_component("매시브 파이어: IRON-B VI (폭발)"))
    usecase.use_component(mechanic_component("호밍 미사일 VI"))
    usecase.use_component(mechanic_component("그라운드 제로"))
    usecase.use_component(mechanic_component("소울 컨트랙트"))
    usecase.use_component(mechanic_component("쓸만한 샤프 아이즈"))
    usecase.use_component(mechanic_component("쓸만한 하이퍼 바디"))
    usecase.use_component(mechanic_component("스파이더 인 미러"))
    usecase.use_component(mechanic_component("크레스트 오브 더 솔라"))
    usecase.use_component(mechanic_component("리스트레인트 링"))
    usecase.use_component(mechanic_component("리스크테이커 링"))
    usecase.use_component(mechanic_component("웨폰퍼프-D 링"))
    usecase.use_component(mechanic_component("윌 오브 리버티"))
    usecase.use_component(mechanic_component("레지스탕스 라인 인팬트리"))
    usecase.use_component(mechanic_component("오버 드라이브"))
    usecase.use_component(mechanic_component("평범한 몬스터"))
    usecase.use_component(mechanic_component("메이플월드 여신의 축복"))

    usecase.listen(
        ("매시브 파이어: IRON-B VI", "use.emitted.global.damage"),
        mechanic_component("매시브 파이어: IRON-B VI (폭발)").reducer("use"),
    )
    usecase.listen(
        ("그라운드 제로", "use.emitted.global.delay"),
        mechanic_component("호밍 미사일 VI").reducer("pause"),
    )

    return usecase
