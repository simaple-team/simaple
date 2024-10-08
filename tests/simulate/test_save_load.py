from simaple.simulate.base import ConcreteStore
from simaple.simulate.component.entity import Cooldown, Lasting, Periodic


def test_store_save_load():
    store = ConcreteStore()

    store.set_entity(
        "dur",
        Lasting(
            time_left=3.0,
            assigned_duration=0.0,
        ),
    )

    store.set_entity(
        "x.cooldown",
        Cooldown(
            time_left=3.0,
        ),
    )

    store.set_entity(
        "y.interval",
        Periodic(
            interval_counter=3.0,
            initial_counter=None,
            interval=8.5,
            time_left=2.0,
            count=13,
        ),
    )

    saved_store = store.save()

    new_store = ConcreteStore()
    new_store.load(saved_store)

    assert store.read_entity("dur", None) == new_store.read_entity("dur", None)
    assert store.read_entity("x.cooldown", None) == new_store.read_entity(
        "x.cooldown", None
    )
    assert store.read_entity("y.interval", None) == new_store.read_entity(
        "y.interval", None
    )
