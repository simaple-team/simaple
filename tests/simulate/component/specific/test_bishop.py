import pytest

from simaple.simulate.component.specific.bishop import (
    DivineMark,
    DivineMinion,
    DivineMinionState,
    HexaAngelRayComponent,
    HexaAngelRayState,
)
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


@pytest.fixture
def hexa_angle_ray_component():
    component = HexaAngelRayComponent(
        id="test",
        name="periodic-damage-component",
        damage=10,
        hit=3,
        delay=30,
        punishing_damage=10,
        punishing_hit=5,
        stack_resolve_amount=12,
        cooldown_duration=0,
        synergy={},
    )
    return component


@pytest.fixture
def hexa_angle_ray_state(
    hexa_angle_ray_component: HexaAngelRayComponent,
    dynamics: Dynamics,
) -> HexaAngelRayState:
    return {
        **hexa_angle_ray_component.get_default_state(),
        "dynamics": dynamics,
        "divine_mark": DivineMark(advantage=None),
    }


def test_hexa_angle_ray(
    hexa_angle_ray_component: HexaAngelRayComponent,
    hexa_angle_ray_state: HexaAngelRayState,
):
    hexa_angle_ray_state, events = hexa_angle_ray_component.use(
        None, hexa_angle_ray_state
    )
    assert count_damage_skill(events) == 1

    for _ in range(10):
        hexa_angle_ray_state, events = hexa_angle_ray_component.stack(
            None, hexa_angle_ray_state
        )
        assert count_damage_skill(events) == 0

    hexa_angle_ray_state, events = hexa_angle_ray_component.stack(
        None, hexa_angle_ray_state
    )
    assert count_damage_skill(events) == 1

    hexa_angle_ray_state, events = hexa_angle_ray_component.stack(
        None, hexa_angle_ray_state
    )
    assert count_damage_skill(events) == 0

    for _ in range(7):
        hexa_angle_ray_state, events = hexa_angle_ray_component.stack(
            None, hexa_angle_ray_state
        )
        assert count_damage_skill(events) == 0


@pytest.fixture
def divine_minion_component():
    component = DivineMinion(
        id="test",
        name="periodic-damage-component",
        cooldown_duration=0,
        damage=10,
        hit=3,
        delay=30,
        periodic_interval=2000,
        periodic_damage=100,
        periodic_hit=100,
        lasting_duration=10000,
        mark_advantage={
            "damage_multiplier": 10,
        },
    )
    return component


@pytest.fixture
def divine_minion_state(
    divine_minion_component: DivineMinion,
    dynamics: Dynamics,
) -> DivineMinionState:
    return {
        **divine_minion_component.get_default_state(),
        "dynamics": dynamics,
        "divine_mark": DivineMark(),
    }


def test_divine_mark(
    divine_minion_component: DivineMinion,
    divine_minion_state: DivineMinionState,
):
    divine_minion_state, events = divine_minion_component.use(None, divine_minion_state)
    divine_minion_state, events = divine_minion_component.elapse(
        300, divine_minion_state
    )
