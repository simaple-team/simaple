from simaple.container.simulation import SimulationEnvironment
from simaple.container.usecase.builtin.common import define_crest_of_the_solar
from simaple.container.usecase.builtin.util import get_component_loader
from simaple.simulate.usecase import Usecase


# fmt: off
def windbreaker_usecase(environment: SimulationEnvironment) -> Usecase:
    component = get_component_loader(environment)
    usecase = Usecase()

    usecase = define_crest_of_the_solar(usecase, component)

    usecase.use_component(component("엘리멘트 : 스톰"))
    usecase.use_component(component("세컨드 윈드"))
    usecase.use_component(component("핀포인트 피어스"))
    usecase.use_component(component("시그너스 나이츠"))
    usecase.use_component(component("샤프 아이즈"))
    usecase.use_component(component("스톰 브링어"))
    usecase.use_component(component("스톰 윔"))
    usecase.use_component(component("글로리 오브 가디언즈"))
    usecase.use_component(component("하울링 게일"))
    usecase.use_component(component("아이들 윔"))
    usecase.use_component(component("윈드 월"))
    usecase.use_component(component("볼텍스 스피어"))
    usecase.use_component(component("가이디드 애로우"))
    usecase.use_component(component("천공의 노래 VI"))
    usecase.use_component(component("트라이플링 윔 VI"))
    usecase.use_component(component("미스트랄 스프링"))
    usecase.use_component(component("소울 컨트랙트"))
    usecase.use_component(component("쓸만한 샤프 아이즈"))
    usecase.use_component(component("쓸만한 하이퍼 바디"))
    usecase.use_component(component("스파이더 인 미러"))
    usecase.use_component(component("리스트레인트 링"))
    usecase.use_component(component("리스크테이커 링"))
    usecase.use_component(component("웨폰퍼프-D 링"))
    usecase.use_component(component("시그너스 팔랑크스"))
    usecase.use_component(component("초월자 시그너스의 축복"))
    usecase.use_component(component("크리티컬 리인포스"))

    usecase.listen(("핀포인트 피어스", "use.emitted.global.damage"), component("스톰 브링어").reducer("trigger"))
    usecase.listen(("천공의 노래", "elapse.emitted.global.damage"), component("스톰 브링어").reducer("trigger"))
    usecase.listen(("천공의 노래", "stop.emitted.global.damage"), component("스톰 브링어").reducer("trigger"))
    usecase.listen(("천공의 노래 VI", "elapse.emitted.global.damage"), component("스톰 브링어").reducer("trigger"))
    usecase.listen(("천공의 노래 VI", "stop.emitted.global.damage"), component("스톰 브링어").reducer("trigger"))
    usecase.listen(("하울링 게일", "elapse.emitted.global.damage"), component("스톰 브링어").reducer("trigger"))
    usecase.listen(("시그너스 팔랑크스", "elapse.emitted.global.damage"), component("스톰 브링어").reducer("trigger"))
    usecase.listen(("볼텍스 스피어", "elapse.emitted.global.damage"), component("스톰 브링어").reducer("trigger"))

    usecase.listen(("핀포인트 피어스", "use.emitted.global.damage"), component("트라이플링 윔 VI").reducer("trigger"))
    usecase.listen(("천공의 노래", "elapse.emitted.global.damage"), component("트라이플링 윔 VI").reducer("trigger"))
    usecase.listen(("천공의 노래", "stop.emitted.global.damage"), component("트라이플링 윔 VI").reducer("trigger"))
    usecase.listen(("천공의 노래 VI", "elapse.emitted.global.damage"), component("트라이플링 윔 VI").reducer("trigger"))
    usecase.listen(("천공의 노래 VI", "stop.emitted.global.damage"), component("트라이플링 윔 VI").reducer("trigger"))
    usecase.listen(("하울링 게일", "elapse.emitted.global.damage"), component("트라이플링 윔 VI").reducer("trigger"))
    usecase.listen(("시그너스 팔랑크스", "elapse.emitted.global.damage"), component("트라이플링 윔 VI").reducer("trigger"))
    usecase.listen(("볼텍스 스피어", "elapse.emitted.global.damage"), component("트라이플링 윔 VI").reducer("trigger"))

    usecase.listen(("핀포인트 피어스", "use.emitted.global.damage"), component("스톰 윔").reducer("trigger"))
    usecase.listen(("천공의 노래", "elapse.emitted.global.damage"), component("스톰 윔").reducer("trigger"))
    usecase.listen(("천공의 노래", "stop.emitted.global.damage"), component("스톰 윔").reducer("trigger"))
    usecase.listen(("천공의 노래 VI", "elapse.emitted.global.damage"), component("스톰 윔").reducer("trigger"))
    usecase.listen(("천공의 노래 VI", "stop.emitted.global.damage"), component("스톰 윔").reducer("trigger"))
    usecase.listen(("하울링 게일", "elapse.emitted.global.damage"), component("스톰 윔").reducer("trigger"))
    usecase.listen(("시그너스 팔랑크스", "elapse.emitted.global.damage"), component("스톰 윔").reducer("trigger"))
    usecase.listen(("볼텍스 스피어", "elapse.emitted.global.damage"), component("스톰 윔").reducer("trigger"))

    usecase.listen(("핀포인트 피어스", "use.emitted.global.damage"), component("윈드 월").reducer("trigger"))
    usecase.listen(("천공의 노래", "elapse.emitted.global.damage"), component("윈드 월").reducer("trigger"))
    usecase.listen(("천공의 노래", "stop.emitted.global.damage"), component("윈드 월").reducer("trigger"))
    usecase.listen(("천공의 노래 VI", "elapse.emitted.global.damage"), component("윈드 월").reducer("trigger"))
    usecase.listen(("천공의 노래 VI", "stop.emitted.global.damage"), component("윈드 월").reducer("trigger"))
    usecase.listen(("하울링 게일", "elapse.emitted.global.damage"), component("윈드 월").reducer("trigger"))
    usecase.listen(("시그너스 팔랑크스", "elapse.emitted.global.damage"), component("윈드 월").reducer("trigger"))
    usecase.listen(("볼텍스 스피어", "elapse.emitted.global.damage"), component("윈드 월").reducer("trigger"))

    return usecase
# fmt: on
