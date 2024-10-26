from simaple.container.simulation import SimulationEnvironment
from simaple.container.usecase.base import Usecase
from simaple.container.usecase.builtin.util import get_component_loader
from simaple.simulate.component.view import (
    BuffParentView,
    InformationParentView,
    KeydownParentView,
    RunningParentView,
    ValidityParentView,
)
from simaple.simulate.kms import bare_store
from simaple.simulate.timer import clock_view, timer_delay_dispatcher


# fmt: off
def archmagefb_engine(environment: SimulationEnvironment):

    component = get_component_loader(environment)
    usecase = Usecase()


    usecase.use_component(component("퍼번트 드레인"))
    usecase.use_component(component("메디테이션"))
    usecase.use_component(component("익스트림 매직(불,독)"))
    usecase.use_component(component("아케인 에임(액티브)"))
    usecase.use_component(component("텔레포트 마스터리"))
    usecase.use_component(component("포이즌 노바"))
    usecase.use_component(component("도트 퍼니셔"))
    usecase.use_component(component("메테오"))
    usecase.use_component(component("메테오(패시브)"))
    usecase.use_component(component("이프리트"))
    usecase.use_component(component("파이어 오라"))
    usecase.use_component(component("이그나이트"))
    usecase.use_component(component("포이즌 미스트"))
    usecase.use_component(component("포이즌 체인"))
    usecase.use_component(component("메기도 플레임"))
    usecase.use_component(component("퓨리 오브 이프리트"))
    usecase.use_component(component("인페르날 베놈"))
    usecase.use_component(component("플레임 스윕 VI"))
    usecase.use_component(component("미스트 이럽션 VI"))
    usecase.use_component(component("플레임 헤이즈 VI"))
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




    usecase.listen(("*", "elapse"), timer_delay_dispatcher)
    usecase.add_view("clock", clock_view)

    usecase.add_view("info", InformationParentView.build(usecase.build_viewset()))
    usecase.add_view("validity", ValidityParentView.build(usecase.build_viewset()))
    usecase.add_view("buff", BuffParentView.build(usecase.build_viewset()))
    usecase.add_view("running", RunningParentView.build(usecase.build_viewset()))
    usecase.add_view("keydown", KeydownParentView.build(usecase.build_viewset()))

    usecase.listen(("미스트 이럽션 VI", "use.emitted.global.damage"), component("플레임 헤이즈 VI").reducer("reset_cooldown"))

    usecase.listen(("미스트 이럽션 VI", "use"), component("포이즌 노바").reducer("trigger"))

    usecase.listen(("플레임 스윕 VI", "use.emitted.global.damage"), component("메테오(패시브)").reducer("use"))
    usecase.listen(("플레임 헤이즈 VI", "use.emitted.global.damage"), component("메테오(패시브)").reducer("use"))
    usecase.listen(("미스트 이럽션 VI", "use.emitted.global.damage"), component("메테오(패시브)").reducer("use"))
    usecase.listen(("이그나이트", "use.emitted.global.damage"), component("메테오(패시브)").reducer("use"))
    usecase.listen(("이프리트", "elapse.emitted.global.damage"), component("메테오(패시브)").reducer("use"))

    usecase.listen(("플레임 스윕 VI", "use.emitted.global.damage"), component("이그나이트").reducer("use"))
    usecase.listen(("플레임 헤이즈 VI", "use.emitted.global.damage"), component("이그나이트").reducer("use"))
    usecase.listen(("도트 퍼니셔", "use.emitted.global.damage"), component("이그나이트").reducer("use"))
    usecase.listen(("퓨리 오브 이프리트", "elapse.emitted.global.damage"), component("이그나이트").reducer("use"))
    usecase.listen(("이프리트", "elapse.emitted.global.damage"), component("이그나이트").reducer("use"))

    usecase.listen(("플레임 헤이즈 VI", "use"), component("포이즌 미스트").reducer("use"))

    usecase.listen(("미스트 이럽션 VI", "use"), component("플레임 스윕 VI").reducer("explode"))

    usecase.listen(("미스트 이럽션 VI", "use.emitted.global.damage"), component("플레임 헤이즈 VI").reducer("reset_cooldown"))

    usecase.listen(("미스트 이럽션 VI", "use.emitted.global.mob"), component("평범한 몬스터").reducer("add_dot"))
    usecase.listen(("포이즌 노바", "use.emitted.global.mob"), component("평범한 몬스터").reducer("add_dot"))
    usecase.listen(("이프리트", "use.emitted.global.mob"), component("평범한 몬스터").reducer("add_dot"))
    usecase.listen(("메기도 플레임", "use.emitted.global.mob"), component("평범한 몬스터").reducer("add_dot"))
    usecase.listen(("플레임 스윕 VI", "use.emitted.global.mob"), component("평범한 몬스터").reducer("add_dot"))
    usecase.listen(("플레임 헤이즈 VI", "use.emitted.global.mob"), component("평범한 몬스터").reducer("add_dot"))
    usecase.listen(("도트 퍼니셔", "use.emitted.global.mob"), component("평범한 몬스터").reducer("add_dot"))

    store = bare_store(environment.character.action_stat)



    return usecase.create_engine(store)
# fmt: on
