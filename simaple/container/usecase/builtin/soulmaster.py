from simaple.container.simulation import SimulationEnvironment
from simaple.container.usecase.builtin.util import get_component_loader
from simaple.simulate.usecase import Usecase
from simaple.container.usecase.builtin.common import define_crest_of_the_solar


# fmt: off
def soulmaster_usecase(environment: SimulationEnvironment) -> Usecase:
    component = get_component_loader(environment)
    usecase = Usecase()

    usecase = define_crest_of_the_solar(usecase, component)

    usecase.use_component(component("엘리멘트: 소울"))
    usecase.use_component(component("솔라 슬래시/루나 디바이드"))
    usecase.use_component(component("크로스 더 스틱스"))
    usecase.use_component(component("엘리시온"))
    usecase.use_component(component("코스믹 버스트"))
    usecase.use_component(component("트루 사이트"))
    usecase.use_component(component("코스믹 샤워"))
    usecase.use_component(component("솔루나 타임"))
    usecase.use_component(component("코스믹 포지"))
    usecase.use_component(component("코스모스"))
    usecase.use_component(component("소울 이클립스"))
    usecase.use_component(component("플레어 슬래시"))
    usecase.use_component(component("소울 컨트랙트"))
    usecase.use_component(component("쓸만한 샤프 아이즈"))
    usecase.use_component(component("쓸만한 하이퍼 바디"))
    usecase.use_component(component("스파이더 인 미러"))
    usecase.use_component(component("리스트레인트 링"))
    usecase.use_component(component("리스크테이커 링"))
    usecase.use_component(component("웨폰퍼프-S 링"))
    usecase.use_component(component("시그너스 팔랑크스"))
    usecase.use_component(component("초월자 시그너스의 축복"))

    usecase.listen(("솔라 슬래시", "use.emitted.global.delay"), component("엘리멘트: 소울").reducer("increase"))
    usecase.listen(("루나 디바이드", "use.emitted.global.delay"), component("엘리멘트: 소울").reducer("increase"))
    usecase.listen(("크로스 더 스틱스", "use.emitted.global.delay"), component("엘리멘트: 소울").reducer("maximize"))
    usecase.listen(("코스믹 포지", "use.emitted.global.delay"), component("엘리멘트: 소울").reducer("maximize"))

    usecase.listen(("크로스 더 스틱스", "use.emitted.global.delay"), component("엘리시온").reducer("crack"))

    usecase.listen(("솔라 슬래시", "use.emitted.global.delay"), component("코스믹 버스트").reducer("trigger"))
    usecase.listen(("루나 디바이드", "use.emitted.global.delay"), component("코스믹 버스트").reducer("trigger"))
    usecase.listen(("크로스 더 스틱스", "use.emitted.global.delay"), component("코스믹 버스트").reducer("trigger"))

    usecase.listen(("솔라 슬래시", "use.emitted.global.delay"), component("플레어 슬래시").reducer("change_stance_trigger"))
    usecase.listen(("루나 디바이드", "use.emitted.global.delay"), component("플레어 슬래시").reducer("change_stance_trigger"))
    usecase.listen(("크로스 더 스틱스", "use.emitted.global.delay"), component("플레어 슬래시").reducer("styx_trigger"))

    return usecase
# fmt: on
