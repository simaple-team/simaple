from typing import Optional

from simaple.simulate.base import Action, Client, Event, EventHandler, State, Store
from simaple.simulate.global_property import Clock
from simaple.simulate.reserved_names import Tag

ACTION_SPENT_TIMER = "global.timer.spent"


def time_elapsing_action(time: float):
    return Action(name="*", method="elapse", payload=time)


class TimerEventHandler(EventHandler):
    """
    Time Handler.
    This handler determine timing policies.
    Handler listens every reserved_names.Tag.DELAY event and judge whether spend it's time
    wholly, or spent partially maybe due to skill-cancelation predication.
    """

    def __call__(
        self, event: Event, _: Store, __: list[Event]
    ) -> Optional[list[Action]]:
        if event.tag in (Tag.DELAY,):
            return [time_elapsing_action(event.payload["time"])]

        return []


def timer_delay_dispatcher(action: Action, store: Store) -> list[Event]:
    """A time-summation dispatcher, which calculates total passed time."""
    if action.method != "elapse" and action.name != "*":
        return []

    time_state, set_time_state = store.use_state("global.time", Clock())

    time_state.spent(action.payload)
    set_time_state(time_state)
    return []


def get_current_time(store: Store) -> float:
    time: float = store.read_state("global.time", Clock()).current_time
    return time


def install_timer(client: Client):
    client.environment.add_dispatcher(timer_delay_dispatcher)
    client.actor.add_handler(TimerEventHandler())
