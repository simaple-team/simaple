from simaple.container.simulation import SimulationEnvironment
from simaple.container.usecase.builtin.common import define_crest_of_the_solar
from simaple.container.usecase.builtin.util import get_component_loader
from simaple.simulate.usecase import Usecase


# fmt: off
def bishop_usecase(environment: SimulationEnvironment) -> Usecase:
    component = get_component_loader(environment)
    usecase = Usecase()

    usecase = define_crest_of_the_solar(usecase, component)

    usecase.use_component(component("파운틴 포 엔젤"))
    usecase.use_component(component("바하뮤트"))
    usecase.use_component(component("어드밴스드 블레스"))
    usecase.use_component(component("아케인 에임(액티브)"))
    usecase.use_component(component("홀리 블러드"))
    usecase.use_component(component("헤븐즈 도어"))
    usecase.use_component(component("프레이"))
    usecase.use_component(component("엔젤 오브 리브라"))
    usecase.use_component(component("엔젤릭 터치"))
    usecase.use_component(component("피스메이커"))
    usecase.use_component(component("디바인 퍼니시먼트"))
    usecase.use_component(component("홀리 어드밴트"))
    usecase.use_component(component("엔젤레이 VI"))
    usecase.use_component(component("트라이엄프 페더 VI"))
    usecase.use_component(component("소울 컨트랙트"))
    usecase.use_component(component("쓸만한 샤프 아이즈"))
    usecase.use_component(component("쓸만한 하이퍼 바디"))
    usecase.use_component(component("스파이더 인 미러"))
    usecase.use_component(component("리스트레인트 링"))
    usecase.use_component(component("리스크테이커 링"))
    usecase.use_component(component("웨폰퍼프-I 링"))
    usecase.use_component(component("오버로드 마나"))
    usecase.use_component(component("에픽 어드벤쳐"))
    usecase.use_component(component("인피니티"))
    usecase.use_component(component("메이플월드 여신의 축복"))
    usecase.use_component(component("제네시스"))
    usecase.use_component(component("평범한 몬스터"))

    #usecase.listen(("엔젤레이", "use.emitted.global.damage"), component("트라이엄프 페더").reducer("trigger"))
    #usecase.listen(("제네시스", "use.emitted.global.damage"), component("트라이엄프 페더").reducer("trigger"))

    usecase.listen(("디바인 퍼니시먼트", "use.emitted.global.damage"), component("엔젤레이 VI").reducer("stack"))

    usecase.listen(("엔젤레이", "use.emitted.global.damage"), component("트라이엄프 페더 VI").reducer("trigger"))
    usecase.listen(("엔젤레이 VI", "use.emitted.global.damage"), component("트라이엄프 페더 VI").reducer("trigger"))
    usecase.listen(("제네시스", "use.emitted.global.damage"), component("트라이엄프 페더 VI").reducer("trigger"))


    return usecase
# fmt: on
