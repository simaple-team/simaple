from simaple.core import Stat
from simaple.simulate.component.specific.archmagefb import (
    FerventDrainStack,
    FlameSwipVI,
    FlameSwipVIState,
    InfernalVenom,
    InfernalVenomState,
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

    state = InfernalVenomState.model_validate(
        {
            **infernal_venom.get_default_state(),
            "dynamics": dynamics,
            "drain_stack": FerventDrainStack(max_count=10, count=10),
        }
    )

    state, events = infernal_venom.use(None, state)

    assert state.drain_stack.get_buff() == Stat(final_damage_multiplier=50)

    state, events = infernal_venom.elapse(10_000, state)
    assert state.drain_stack.get_buff() == Stat(final_damage_multiplier=50)

    state, events = infernal_venom.elapse(15_000, state)
    assert state.drain_stack.get_buff() == Stat(final_damage_multiplier=25)


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
    state = FlameSwipVIState.model_validate(
        {
            **flame_swip_vi.get_default_state(),
            "dynamics": dynamics,
        }
    )

    state, events = flame_swip_vi.use(None, state)
    assert count_damage_skill(events) == 1

    state, events = flame_swip_vi.explode(None, state)
    assert count_damage_skill(events) == 0

    state, events = flame_swip_vi.use(None, state)
    state, events = flame_swip_vi.use(None, state)
    state, events = flame_swip_vi.explode(None, state)

    assert count_damage_skill(events) == 1
