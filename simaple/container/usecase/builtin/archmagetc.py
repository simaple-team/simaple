from simaple.container.simulation import SimulationEnvironment
from simaple.container.usecase.builtin.util import get_component_loader
from simaple.simulate.usecase import Usecase


# fmt: off
def archmagetc_usecase(environment: SimulationEnvironment):

    component = get_component_loader(environment)
    usecase = Usecase()

    usecase.use_component(component("프로스트 이펙트"))
    usecase.use_component(component("익스트림 매직(썬,콜)"))
    usecase.use_component(component("아케인 에임(액티브)"))
    usecase.use_component(component("메디테이션"))
    usecase.use_component(component("엘퀴네스"))
    usecase.use_component(component("아이스 오라"))
    usecase.use_component(component("라이트닝 스피어"))
    usecase.use_component(component("아이스 에이지"))
    usecase.use_component(component("썬더 브레이크"))
    usecase.use_component(component("스피릿 오브 스노우"))
    usecase.use_component(component("주피터 썬더"))
    usecase.use_component(component("프로즌 라이트닝"))
    usecase.use_component(component("체인 라이트닝 VI"))
    usecase.use_component(component("프로즌 오브 VI"))
    usecase.use_component(component("블리자드 VI"))
    usecase.use_component(component("블리자드 VI(패시브)"))
    usecase.use_component(component("소울 컨트랙트"))
    usecase.use_component(component("쓸만한 샤프 아이즈"))
    usecase.use_component(component("쓸만한 하이퍼 바디"))
    usecase.use_component(component("스파이더 인 미러"))
    usecase.use_component(component("크레스트 오브 더 솔라"))
    usecase.use_component(component("리스트레인트 링"))
    usecase.use_component(component("리스크테이커 링"))
    usecase.use_component(component("웨폰퍼프-I 링"))
    usecase.use_component(component("오버로드 마나"))
    usecase.use_component(component("에픽 어드벤쳐"))
    usecase.use_component(component("인피니티"))
    usecase.use_component(component("메이플월드 여신의 축복"))
    usecase.use_component(component("평범한 몬스터"))

    usecase.listen(("프로즌 오브 VI", "elapse.emitted.global.damage"), component("프로스트 이펙트").reducer("increase_step"))
    usecase.listen(("블리자드", "use.emitted.global.damage"), component("프로스트 이펙트").reducer("increase_step"))
    usecase.listen(("엘퀴네스", "elapse.emitted.global.damage"), component("프로스트 이펙트").reducer("increase_step"))
    usecase.listen(("아이스 오라", "elapse.emitted.global.damage"), component("프로스트 이펙트").reducer("increase_step"))
    usecase.listen(("아이스 에이지", "elapse.emitted.global.damage"), component("프로스트 이펙트").reducer("increase_step"))
    usecase.listen(("스피릿 오브 스노우", "elapse.emitted.global.damage"), component("프로스트 이펙트").reducer("increase_three"))

    #usecase.listen(("체인 라이트닝 VI", "use.emitted.global.damage"), component("블리자드(패시브)").reducer("use"))
    #usecase.listen(("프로즌 오브 VI", "use.emitted.global.damage"), component("블리자드(패시브)").reducer("use"))

    usecase.listen(("체인 라이트닝 VI", "use.emitted.global.damage"), component("블리자드 VI(패시브)").reducer("use"))
    usecase.listen(("프로즌 오브 VI", "elapse.emitted.global.damage"), component("블리자드 VI(패시브)").reducer("use"))


    return usecase
# fmt: on
