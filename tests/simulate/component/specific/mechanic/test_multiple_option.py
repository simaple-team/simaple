# pylint: disable=W0621
from functools import partial

import pytest

from simaple.simulate.component.specific.mechanic import (
    MultipleOptionComponent,
    MultipleOptionState,
    RobotMastery,
)
from simaple.simulate.global_property import Dynamics
from simaple.simulate.reserved_names import Tag
from tests.simulate.component.util import pipe


@pytest.mark.parametrize("missile_damage, gatling_damage", [(200, 50)])
class TestMultipleOption:
    @pytest.fixture(name="multiple_option")
    def fixture_multiple_option(self, missile_damage, gatling_damage):
        return MultipleOptionComponent(
            id="test",
            name="test-multiple-option",
            cooldown_duration=40_000,
            delay=690,
            periodic_interval=1000,
            lasting_duration=120_000,
            missile_count=3,
            missile_damage=missile_damage,
            missile_hit=3,
            gatling_count=5,
            gatling_damage=gatling_damage,
            gatling_hit=10,
        )

    @pytest.fixture(name="multiple_option_state")
    def multiple_option_state(
        self,
        multiple_option: MultipleOptionComponent,
        dynamics: Dynamics,
        robot_mastery: RobotMastery,
    ):
        return MultipleOptionState.parse_obj(
            {
                **multiple_option.get_default_state(),
                "dynamics": dynamics,
                "robot_mastery": robot_mastery,
            }
        )

    def test_multiple_option_little_use(
        self,
        multiple_option: MultipleOptionComponent,
        multiple_option_state: MultipleOptionState,
    ):
        # when
        state, _ = multiple_option.use(None, multiple_option_state)
        state, events = multiple_option.elapse(3_000, state)

        # then
        dealing_count = sum([e.tag == Tag.DAMAGE for e in events])
        assert dealing_count == 3

    def test_multiple_option_many_use(
        self,
        multiple_option: MultipleOptionComponent,
        multiple_option_state: MultipleOptionState,
        missile_damage: float,
        gatling_damage: float,
    ):
        # when
        state, _ = multiple_option.use(None, multiple_option_state)
        state, events = multiple_option.elapse(8_000, state)

        # then
        dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

        assert sum([e.payload["damage"] == missile_damage for e in dealing_event]) == 3
        assert sum([e.payload["damage"] == gatling_damage for e in dealing_event]) == 5

    def test_multiple_option_discontinuous_use(
        self,
        multiple_option: MultipleOptionComponent,
        multiple_option_state: MultipleOptionState,
        missile_damage: float,
        gatling_damage: float,
    ):
        # when
        _, events = pipe(
            multiple_option_state,
            partial(multiple_option.use, None),
            partial(multiple_option.elapse, 1300),
            partial(multiple_option.elapse, 4000),
            partial(multiple_option.elapse, 2700),
        )

        # then
        dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

        assert sum([e.payload["damage"] == missile_damage for e in dealing_event]) == 3
        assert sum([e.payload["damage"] == gatling_damage for e in dealing_event]) == 5

    def test_multiple_option_larger_than_period(
        self,
        multiple_option: MultipleOptionComponent,
        multiple_option_state: MultipleOptionState,
        missile_damage: float,
        gatling_damage: float,
    ):
        # when
        state, _ = multiple_option.use(None, multiple_option_state)
        state, events = multiple_option.elapse(14_000, state)

        # then
        dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

        assert (
            sum([e.payload["damage"] == missile_damage for e in dealing_event]) == 3 + 3
        )
        assert (
            sum([e.payload["damage"] == gatling_damage for e in dealing_event]) == 5 + 3
        )
