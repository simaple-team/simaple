from simaple.simulate.base import Action, Client, Event, Store
from simaple.simulate.global_property import Clock


def timer_delay_dispatcher(action: Action, store: Store) -> list[Event]:
    """A time-summation dispatcher, which calculates total passed time."""
    if action.method != "elapse" and action.name != "*":
        return []

    clock, set_clock = store.use_entity("global.time", Clock())

    clock.spent(action.payload)
    set_clock(clock)
    return []


def clock_view(store: Store) -> float:
    time: float = store.read_entity("global.time", Clock()).current_time
    return time


def install_timer(client: Client):
    client.environment.add_dispatcher(timer_delay_dispatcher)
