import pytest

from simaple.simulate.component.specific.soulmaster import Elysion, ElysionState
from simaple.simulate.global_property import Dynamics
from tests.simulate.component.util import count_damage_skill


@pytest.fixture(name="elysion")
def fixture_elysion():
    return Elysion(
        id="test",
        name="test-elysion",
        cooldown_duration=200_000,
        delay=690,
        lasting_duration=30_000,
        crack_damage=200,
        crack_hit=5,
        crack_cooldown=5_000,
        crack_duration=10_000,
        maximum_crack_count=7,
    )


@pytest.fixture(name="elysion_state")
def fixture_elysion_state(
    elysion: Elysion,
    dynamics: Dynamics,
):
    return {
        **elysion.get_default_state(),
        "dynamics": dynamics,
    }


def test_elysion_scenario(elysion: Elysion, elysion_state: ElysionState):
    state, _ = elysion.use(None, elysion_state)

    for _ in range(6):
        state, events = elysion.crack(None, state)
        assert count_damage_skill(events) == 0

    state, events = elysion.crack(None, state)
    assert count_damage_skill(events) == 1


def test_elysion_without_elapse_stuck(elysion: Elysion, elysion_state: ElysionState):
    state, _ = elysion.use(None, elysion_state)

    for _ in range(6):
        state, events = elysion.crack(None, state)
        assert count_damage_skill(events) == 0

    state, events = elysion.crack(None, state)

    for _ in range(30):
        state, events = elysion.crack(None, state)
        assert count_damage_skill(events) == 0


def test_elysion_with_elapse_operates(elysion: Elysion, elysion_state: ElysionState):
    state, _ = elysion.use(None, elysion_state)

    for _ in range(6):
        state, events = elysion.crack(None, state)
        assert count_damage_skill(events) == 0

    state, events = elysion.crack(None, state)
    state, events = elysion.elapse(4500, state)

    for _ in range(12):
        state, events = elysion.crack(None, state)
        assert count_damage_skill(events) == 0

    state, events = elysion.elapse(500, state)
    for _ in range(6):
        state, events = elysion.crack(None, state)
        assert count_damage_skill(events) == 0

    state, events = elysion.crack(None, state)
    assert count_damage_skill(events) == 1


def test_elysion_turn_off(elysion: Elysion, elysion_state: ElysionState):
    state, _ = elysion.use(None, elysion_state)
    state, events = elysion.elapse(40_000, state)

    for _ in range(6):
        state, events = elysion.crack(None, state)
        assert count_damage_skill(events) == 0

    state, events = elysion.crack(None, state)
    assert count_damage_skill(events) == 0
