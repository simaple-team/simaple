from simaple.container.usecase.builtin.util import ComponentFunc
from simaple.simulate.usecase import Usecase


def define_crest_of_the_solar(usecase: Usecase, component: ComponentFunc) -> Usecase:
    usecase.use_component(component("크레스트 오브 더 솔라"))
    usecase.use_component(component("크레스트 오브 더 솔라 (불꽃의 문양)"))

    usecase.listen(
        ("크레스트 오브 더 솔라", "use.emitted.global.damage"),
        component("크레스트 오브 더 솔라 (불꽃의 문양)").reducer("use"),
    )
    return usecase
