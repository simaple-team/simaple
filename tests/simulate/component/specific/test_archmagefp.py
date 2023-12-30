from typing import Optional

from simaple.core import Stat
from simaple.simulate.component.specific.archmagefb import (
    FerventDrain,
    FerventDrainStack,
    FerventDrainState,
    InfernalVenom,
    InfernalVenomState,
)
from simaple.simulate.global_property import Dynamics


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
            "fervent_stack": FerventDrainStack(max_count=10, count=10),
        }
    )

    state, events = infernal_venom.use(state)

    assert state.fervent_stack.get_buff() == Stat(final_damage_multiplier=50)

    state, events = infernal_venom.elapse(10_000, state)
    assert state.fervent_stack.get_buff() == Stat(final_damage_multiplier=50)

    state, events = infernal_venom.elapse(15_000, state)
    assert state.fervent_stack.get_buff() == Stat(final_damage_multiplier=25)
