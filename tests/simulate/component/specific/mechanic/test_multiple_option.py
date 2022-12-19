import pytest

from simaple.simulate.component.specific.mechanic import MultipleOptionComponent
from simaple.simulate.reserved_names import Tag


@pytest.mark.parametrize("missile_damage, gatling_damage", [(200, 50)])
class TestMultipleOption:
    @pytest.fixture(name="multiple_option")
    def fixture_multiple_option(self, mechanic_store, missile_damage, gatling_damage):
        component = MultipleOptionComponent(
            name="test-multiple-option",
            cooldown=40_000,
            delay=690,
            tick_interval=1000,
            duration=120_000,
            missile_count=3,
            missile_damage=missile_damage,
            missile_hit=3,
            gatling_count=5,
            gatling_damage=gatling_damage,
            gatling_hit=10,
        )
        return component.compile(mechanic_store)

    def test_multiple_option_little_use(self, multiple_option):
        multiple_option.use(None)
        events = multiple_option.elapse(3_000)

        dealing_count = sum([e.tag == Tag.DAMAGE for e in events])

        assert dealing_count == 3

    def test_multiple_option_many_use(
        self, multiple_option, missile_damage, gatling_damage
    ):
        multiple_option.use(None)
        events = multiple_option.elapse(8_000)

        dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

        assert sum([e.payload["damage"] == missile_damage for e in dealing_event]) == 3
        assert sum([e.payload["damage"] == gatling_damage for e in dealing_event]) == 5

    def test_multiple_option_discontinuouse_use(
        self, multiple_option, missile_damage, gatling_damage
    ):
        multiple_option.use(None)
        events = []
        events += multiple_option.elapse(1300)
        events += multiple_option.elapse(4000)
        events += multiple_option.elapse(2700)

        dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

        assert sum([e.payload["damage"] == missile_damage for e in dealing_event]) == 3
        assert sum([e.payload["damage"] == gatling_damage for e in dealing_event]) == 5

    def test_multiple_option_larger_than_period(
        self, multiple_option, missile_damage, gatling_damage
    ):
        multiple_option.use(None)
        events = multiple_option.elapse(14_000)

        dealing_event = [e for e in events if e.tag == Tag.DAMAGE]

        assert (
            sum([e.payload["damage"] == missile_damage for e in dealing_event]) == 3 + 3
        )
        assert (
            sum([e.payload["damage"] == gatling_damage for e in dealing_event]) == 5 + 3
        )
