from simaple.container.simulation import SimulationEnvironment
from simaple.container.usecase.builtin.util import get_component_loader
from simaple.simulate.usecase import Usecase


# fmt: off
def dualblade_usecase(environment: SimulationEnvironment):
    component = get_component_loader(environment)
    usecase = Usecase()

    usecase.use_component(component("써든레이드"))
    usecase.use_component(component("파이널 컷"))
    usecase.use_component(component("파이널 컷(버프)"))
    usecase.use_component(component("플래시 뱅"))
    usecase.use_component(component("플래시 뱅(버프)"))
    usecase.use_component(component("히든 블레이드"))
    usecase.use_component(component("블레이드 스톰"))
    usecase.use_component(component("카르마 퓨리"))
    usecase.use_component(component("블레이드 토네이도"))
    usecase.use_component(component("헌티드 엣지 - 나찰"))
    usecase.use_component(component("얼티밋 다크 사이트"))
    usecase.use_component(component("팬텀 블로우 VI"))
    usecase.use_component(component("아수라 VI"))
    usecase.use_component(component("카르마 블레이드"))
    usecase.use_component(component("카르마 블레이드 (업보의 칼날)"))
    usecase.use_component(component("소울 컨트랙트"))
    usecase.use_component(component("쓸만한 샤프 아이즈"))
    usecase.use_component(component("쓸만한 하이퍼 바디"))
    usecase.use_component(component("스파이더 인 미러"))
    usecase.use_component(component("크레스트 오브 더 솔라"))
    usecase.use_component(component("리스트레인트 링"))
    usecase.use_component(component("리스크테이커 링"))
    usecase.use_component(component("웨폰퍼프-L 링"))
    usecase.use_component(component("에픽 어드벤쳐"))
    usecase.use_component(component("메이플월드 여신의 축복"))
    usecase.use_component(component("레디 투 다이"))

    usecase.listen(("써든레이드", "use.emitted.global.delay"), component("파이널 컷").reducer("sudden_raid"))

    usecase.listen(("파이널 컷", "use.emitted.global.damage"), component("파이널 컷(버프)").reducer("use"))
    usecase.listen(("플래시 뱅", "use.emitted.global.delay"), component("플래시 뱅(버프)").reducer("use"))

    usecase.listen(("아수라", "elapse.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("아수라 VI", "elapse.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("팬텀 블로우", "use.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("팬텀 블로우 VI", "use.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("써든레이드", "use.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("플래시 뱅", "use.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("파이널 컷", "use.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("블레이드 스톰", "use.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("블레이드 스톰", "elapse.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("카르마 퓨리", "elapse.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("블레이드 토네이도", "use.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("블레이드 토네이도", "elapse.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))
    usecase.listen(("헌티드 엣지 - 나찰", "use.emitted.global.damage"), component("히든 블레이드").reducer("trigger"))

    usecase.listen(("팬텀 블로우", "use.emitted.global.damage"), component("헌티드 엣지 - 나찰").reducer("use"))
    usecase.listen(("팬텀 블로우 VI", "use.emitted.global.damage"), component("헌티드 엣지 - 나찰").reducer("use"))

    usecase.listen(("카르마 블레이드", "use.done.global.delay"), component("카르마 블레이드 (업보의 칼날)").reducer("use"))
    usecase.listen(("아수라", "elapse.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("아수라 VI", "elapse.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("팬텀 블로우", "use.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("팬텀 블로우 VI", "use.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("써든레이드", "use.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("플래시 뱅", "use.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("파이널 컷", "use.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("블레이드 스톰", "use.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("블레이드 스톰", "elapse.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("카르마 퓨리", "elapse.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("블레이드 토네이도", "use.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("블레이드 토네이도", "elapse.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))
    usecase.listen(("헌티드 엣지 - 나찰", "use.emitted.global.damage"), component("카르마 블레이드 (업보의 칼날)").reducer("trigger"))


    return usecase
# fmt: on
