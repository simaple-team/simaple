# pylint: disable=W0621
import pytest

from simaple.core import Stat
from simaple.simulate.component.skill import StackableBuffSkillComponent


@pytest.fixture
def buff_component(bare_store):
    component = StackableBuffSkillComponent(
        name="buff-component",
        stat=Stat(attack_power=30),
        cooldown=30_000,
        delay=600,
        duration=15_000,
        maximum_stack=2,
    )
    return component.compile(bare_store)


def test_use_buff_component(buff_component):
    buff_component.use(None)
    assert buff_component.buff() == Stat(attack_power=30)


def test_use_buff_component_twice(buff_component):
    buff_component.use(None)
    buff_component.use(None)
    assert buff_component.buff() == Stat(attack_power=60)


def test_use_buff_component_remains(buff_component):
    buff_component.use(None)
    buff_component.elapse(10_000)
    assert buff_component.buff() == Stat(attack_power=30)


def test_use_buff_component_turns_off(buff_component):
    buff_component.use(None)
    buff_component.elapse(20_000)
    assert buff_component.buff() is None


def test_buff_skill_use_forbidden(buff_component):
    buff_component.use(None)
    buff_component.elapse(20_000)
    events = buff_component.use(None)
    assert buff_component.buff() is None
