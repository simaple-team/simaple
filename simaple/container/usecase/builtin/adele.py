from simaple.container.simulation import SimulationEnvironment
from simaple.container.usecase.builtin.util import get_component_loader
from simaple.simulate.usecase import Usecase
from simaple.container.usecase.builtin.common import define_crest_of_the_solar


# fmt: off
def adele_usecase(environment: SimulationEnvironment) -> Usecase:
    component = get_component_loader(environment)
    usecase = Usecase()

    usecase = define_crest_of_the_solar(usecase, component)

    usecase.use_component(component("에테르"))
    usecase.use_component(component("레조넌스"))
    usecase.use_component(component("레조넌스(버프)"))
    usecase.use_component(component("크리에이션"))
    usecase.use_component(component("테리토리"))
    usecase.use_component(component("게더링"))
    usecase.use_component(component("게더링(디버프)"))
    usecase.use_component(component("블로섬"))
    usecase.use_component(component("그레이브"))
    usecase.use_component(component("그레이브(디버프)"))
    usecase.use_component(component("마커"))
    usecase.use_component(component("루인"))
    usecase.use_component(component("인피니트"))
    usecase.use_component(component("리스토어"))
    usecase.use_component(component("리스토어(버프)"))
    usecase.use_component(component("스톰"))
    usecase.use_component(component("마에스트로"))
    usecase.use_component(component("디바이드 VI"))
    usecase.use_component(component("샤드 VI"))
    usecase.use_component(component("원더 VI"))
    usecase.use_component(component("오더 VI"))
    usecase.use_component(component("소울 컨트랙트"))
    usecase.use_component(component("쓸만한 샤프 아이즈"))
    usecase.use_component(component("쓸만한 하이퍼 바디"))
    usecase.use_component(component("스파이더 인 미러"))
    usecase.use_component(component("리스트레인트 링"))
    usecase.use_component(component("리스크테이커 링"))
    usecase.use_component(component("레이스 오브 갓"))
    usecase.use_component(component("매직 서킷 풀드라이브"))
    usecase.use_component(component("그란디스 여신의 축복(레프)"))
    usecase.use_component(component("웨폰퍼프-S 링"))


    usecase.listen(("디바이드", "use.emitted.global.damage"), component("에테르").reducer("trigger"))
    usecase.listen(("디바이드 VI", "use.emitted.global.damage"), component("에테르").reducer("trigger"))
    usecase.listen(("레조넌스", "use.emitted.global.damage"), component("에테르").reducer("resonance"))
    usecase.listen(("오더", "use.emitted.global.damage"), component("에테르").reducer("order"))
    usecase.listen(("오더 VI", "use.emitted.global.damage"), component("에테르").reducer("order"))

    #usecase.listen(("디바이드", "use.emitted.global.damage"), component("원더").reducer("use_with_ignore_reject"))
    #usecase.listen(("디바이드 VI", "use.emitted.global.damage"), component("원더").reducer("use_with_ignore_reject"))

    usecase.listen(("디바이드", "use.emitted.global.damage"), component("원더 VI").reducer("use_with_ignore_reject"))
    usecase.listen(("디바이드 VI", "use.emitted.global.damage"), component("원더 VI").reducer("use_with_ignore_reject"))

    usecase.listen(("레조넌스", "use.emitted.global.damage"), component("레조넌스(버프)").reducer("use"))

    usecase.listen(("디바이드", "use.emitted.global.damage"), component("크리에이션").reducer("trigger"))
    usecase.listen(("디바이드 VI", "use.emitted.global.damage"), component("크리에이션").reducer("trigger"))

    usecase.listen(("게더링", "use.emitted.global.damage"), component("게더링(디버프)").reducer("use"))

    usecase.listen(("그레이브", "use.emitted.global.damage"), component("그레이브(디버프)").reducer("use"))
    usecase.listen(("리스토어", "use.emitted.global.delay"), component("리스토어(버프)").reducer("use"))

    return usecase
# fmt: on
