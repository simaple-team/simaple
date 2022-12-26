from simaple.simulate.base import ConcreteStore
from simaple.simulate.component.state_fragment import (
    CooldownState,
    DurationState,
    IntervalState,
)


def test_store_save_load():
    store = ConcreteStore()

    store.set_state(
        "dur",
        DurationState(
            time_left=3.0,
            assigned_duration=0.0,
        ),
    )

    store.set_state(
        "x.cooldown",
        CooldownState(
            time_left=3.0,
        ),
    )

    store.set_state(
        "y.interval",
        IntervalState(
            interval_counter=3.0,
            interval=8.5,
            interval_time_left=2.0,
            count=13,
        ),
    )

    saved_store = store.save()

    new_store = ConcreteStore()
    new_store.load(saved_store)

    assert store.read_state("dur", None) == new_store.read_state("dur", None)
    assert store.read_state("x.cooldown", None) == new_store.read_state(
        "x.cooldown", None
    )
    assert store.read_state("y.interval", None) == new_store.read_state(
        "y.interval", None
    )
