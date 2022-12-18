import pytest

from simaple.core.base import Stat
from simaple.simulate.component.specific.archmagetc import ThunderAttackSkillComponent
from simaple.simulate.reserved_names import Tag


@pytest.fixture(name="thunder_attack_skill")
def fixture_thunder_attack_skill(frost_effect, archmagetc_store):
    component = ThunderAttackSkillComponent(
        name="test-component",
        damage=130,
        delay=500,
        hit=3,
        cooldown=0,
    )
    return component.compile(archmagetc_store)


def test_frost_effect_reducer(frost_effect):
    frost_effect.increase_step(None)
    new_stack = frost_effect.frost_stack.get_stack()

    assert frost_effect.buff() == Stat(critical_damage=3)


def test_with_no_stack(frost_effect, thunder_attack_skill):
    events = thunder_attack_skill.use(None)
    damage_events = [e for e in events if e.tag == Tag.DAMAGE]

    assert damage_events[0].payload["modifier"] == Stat()


def test_with_some_stack(frost_effect, thunder_attack_skill):
    for _ in range(3):
        frost_effect.increase_step(None)

    events = thunder_attack_skill.use(None)
    damage_events = [e for e in events if e.tag == Tag.DAMAGE]

    assert damage_events[0].payload["modifier"] == Stat(damage_multiplier=12 * 3)
