# pylint: disable=W0621
import pytest

from simaple.simulate.component.hexa_skill import (
    PeriodicDamageConfiguratedHexaSkillComponent,
    PeriodicDamageHexaState,
)
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag


@pytest.fixture
def periodic_damage_component():
    component = PeriodicDamageConfiguratedHexaSkillComponent(
        id="test",
        name="periodic-damage-component",
        damage_and_hits=[{"damage": 100, "hit": 1}, {"damage": 200, "hit": 3}],
        delay=30,
        periodic_interval=120,
        periodic_damage=50,
        periodic_hit=3,
        lasting_duration=1_000,
        cooldown_duration=30_000,
    )
    return component


@pytest.fixture
def periodic_damage_state(
    periodic_damage_component: PeriodicDamageConfiguratedHexaSkillComponent,
    dynamics: Dynamics,
):
    return PeriodicDamageHexaState.model_validate(
        {
            **periodic_damage_component.get_default_state(),
            "dynamics": dynamics,
        }
    )


def test_periodic_damage_component_emit_initial_damage(
    periodic_damage_component: PeriodicDamageConfiguratedHexaSkillComponent,
    periodic_damage_state: PeriodicDamageHexaState,
):
    # given
    _, events = periodic_damage_component.use(None, periodic_damage_state)

    # then
    assert events[0]["payload"] == {"damage": 100, "hit": 1.0, "modifier": None}
    assert events[1]["payload"] == {"damage": 200, "hit": 3.0, "modifier": None}
    assert events[2]["payload"] == {"time": 30.0}
