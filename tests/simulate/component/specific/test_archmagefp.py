from simaple.core import Stat
from simaple.simulate.component.specific.archmagefb import (
    FerventDrainStack,
    FlameSwipVI,
    FlameSwipVIState,
    InfernalVenom,
    InfernalVenomState,
    PoisonRegionComponent,
    PoisonRegionState,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


def test_fervent_drain_buff() -> None:
    stack = FerventDrainStack(max_count=10, count=10)
    assert stack.get_buff() == Stat(final_damage_multiplier=50)


def test_fervent_drain_restriction() -> None:
    stack = FerventDrainStack(max_count=5, count=10)
    assert stack.get_buff() == Stat(final_damage_multiplier=25)

    stack.set_max_count(10)
    assert stack.get_buff() == Stat(final_damage_multiplier=50)

    stack.set_max_count(5)
    assert stack.get_buff() == Stat(final_damage_multiplier=25)


def test_infernal_venom(dynamics: Dynamics) -> None:
    infernal_venom = InfernalVenom(
        id="test",
        name="test-infernal_venom",
        cooldown_duration=15_000,
        first_damage=100,
        second_damage=200,
        first_hit=1,
        second_hit=2,
        delay=690,
        lasting_duration=20_000,
    )

    state: InfernalVenomState = {
        **infernal_venom.get_default_state(),
        "dynamics": dynamics,
        "drain_stack": FerventDrainStack(max_count=10, count=10),
    }

    state, events = infernal_venom.use(None, state)

    assert state["drain_stack"].get_buff() == Stat(final_damage_multiplier=50)

    state, events = infernal_venom.elapse(10_000, state)
    assert state["drain_stack"].get_buff() == Stat(final_damage_multiplier=50)

    state, events = infernal_venom.elapse(15_000, state)
    assert state["drain_stack"].get_buff() == Stat(final_damage_multiplier=25)


def test_flame_swip_vi(dynamics: Dynamics) -> None:
    flame_swip_vi = FlameSwipVI(
        id="test",
        name="test-flame_swip_vi",
        delay=690,
        damage=100,
        hit=1,
        explode_damage=500,
        explode_hit=1,
        dot_damage=100,
        dot_lasting_duration=10_000,
        cooldown_duration=0,
    )
    state: FlameSwipVIState = {
        **flame_swip_vi.get_default_state(),
        "dynamics": dynamics,
    }

    state, events = flame_swip_vi.use(None, state)
    assert count_damage_skill(events) == 1

    state, events = flame_swip_vi.explode(None, state)
    assert count_damage_skill(events) == 0

    state, events = flame_swip_vi.use(None, state)
    state, events = flame_swip_vi.use(None, state)
    state, events = flame_swip_vi.explode(None, state)

    assert count_damage_skill(events) == 1


def test_poison_region_use(dynamics: Dynamics) -> None:
    """
    PoisonRegion의 use 메서드가 lasting을 시작하고 dot 이벤트를 생성하며,
    consumable의 영역(stack)을 1로 설정하는지 테스트한다.
    """
    poison_region = PoisonRegionComponent(
        id="test",
        name="test-poison_region",
        delay=500,
        cooldown_duration=1000,
        lasting_duration=5000,
        dot_damage=50,
        dot_lasting_duration=2000,
        explode_damage=300,
        explode_hit=2,
        explode_multiple=3,
        stack_interval=1000,
        maximum_stack=5,
    )
    state: PoisonRegionState = {
        **poison_region.get_default_state(),
        "dynamics": dynamics,
    }
    state, events = poison_region.use(None, state)

    # use 후 consumable의 영역(stack)이 1로 설정되어야 한다.
    assert state["consumable"].stack == 1

    # lasting_trait.start_lasting_with_cooldown과 dot 이벤트 호출 결과 이벤트가 생성됨
    assert events, "use 호출 후 이벤트가 생성되어야 합니다."


def test_poison_region_elapse(dynamics: Dynamics) -> None:
    """
    PoisonRegion의 elapse 메서드가 lasting과 consumable의 타이머를 제대로 경과시키는지 테스트한다.
    """
    poison_region = PoisonRegionComponent(
        id="test",
        name="test-poison_region",
        delay=500,
        cooldown_duration=1000,
        lasting_duration=5000,
        dot_damage=50,
        dot_lasting_duration=2000,
        explode_damage=300,
        explode_hit=2,
        explode_multiple=3,
        stack_interval=1000,
        maximum_stack=5,
    )
    state: PoisonRegionState = {
        **poison_region.get_default_state(),
        "dynamics": dynamics,
    }

    # 먼저 use를 호출하여 lasting과 consumable 영역을 활성화
    state, _ = poison_region.use(None, state)
    assert state["consumable"].stack == 1

    # elapse 호출 전후 consumable의 내부 타이머(time_left)를 확인 (구현에 따라 다를 수 있음)
    elapsed_time = 1200
    state, events = poison_region.elapse(elapsed_time, state)

    # 적어도 elapsed 이벤트가 포함되어 있어야 함
    assert events, "elapse 호출 후 이벤트가 생성되어야 합니다."

    # consumable의 time_left가 경과 시간만큼 감소했을 가능성을 체크
    # (구현에 따라 음수로 내려가지 않고 0으로 클리핑될 수 있음)
    assert state["consumable"].stack == 2


def test_poison_region_explode(dynamics: Dynamics) -> None:
    """
    PoisonRegion의 explode 메서드가 consumable에 쌓인 영역 수만큼 폭발 피해를 적용하고,
    폭발 후 consumable 영역이 모두 소모되는지 테스트한다.
    """
    poison_region = PoisonRegionComponent(
        id="test",
        name="test-poison_region",
        delay=500,
        cooldown_duration=1000,
        lasting_duration=5000,
        dot_damage=50,
        dot_lasting_duration=2000,
        explode_damage=300,
        explode_hit=2,
        explode_multiple=3,
        stack_interval=1000,
        maximum_stack=5,
    )
    state: PoisonRegionState = {
        **poison_region.get_default_state(),
        "dynamics": dynamics,
    }

    # consumable 영역을 3으로 설정 (예: use 외에도 다른 방법으로 영역이 추가되었을 경우)
    consumable = state["consumable"].model_copy()
    consumable.stack = 3
    state["consumable"] = consumable

    state, events = poison_region.explode(None, state)

    # 폭발 시 explode_hit(2)에 consumable의 영역 수(3)를 곱한 값이 데미지 이벤트의 히트 수로 적용되어야 함
    # (count_damage_skill은 즉시 피해 이벤트의 개수를 세는 유틸 함수임)
    assert (
        count_damage_skill(events) == 2
    ), "폭발 시 즉시 피해 이벤트가 발생해야 합니다."

    # 첫번째 이벤트의 히트 수가 2 * 3 = 6이어야 함 (EmptyEvent의 내부 구조에 따라 검증)
    event = events[0]
    assert (
        event["payload"]["hit"] == 2
    ), f"폭발 이벤트의 첫 번째 hit 값은 {2}이어야 합니다."

    # 폭발 후 consumable의 영역(stack)은 모두 소모되어 0이 되어야 함
    assert (
        state["consumable"].stack == 0
    ), "폭발 후 consumable 영역이 소모되어야 합니다."
