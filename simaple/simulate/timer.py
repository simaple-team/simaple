from typing import Optional

from simaple.simulate.base import Action, Client, Event, EventHandler, State, Store
from simaple.simulate.reserved_names import Tag

ACTION_SPENT_TIMER = "global.timer.spent"


class TimerEventHandler(EventHandler):
    """
    Time Handler.
    This handler determine timing policies.
    Handler listens every reserved_names.Tag.DELAY event and judge whether spend it's time
    wholly, or spent partially maybe due to skill-cancelation predication.
    """

    def __call__(self, event: Event) -> Optional[list[Action]]:
        if event.tag in (Tag.DELAY,):
            return [Action(name="*", method="elapse", payload=event.payload["time"])]

        return []


class TimeState(State):
    current_time: float = 0

    def spent(self, time: float):
        self.current_time += time


def timer_delay_dispatcher(action: Action, store: Store) -> tuple[Event]:
    """A time-summation dispatcher, which calculates total passed time."""
    if action.method != "elapse":
        return []

    time_state, set_time_state = store.use_state("global.time", TimeState())

    time_state.spent(action.payload)
    set_time_state(time_state)
    return []


def install_timer(client: Client):
    client.reducer.add_reducer(timer_delay_dispatcher)
    client.actor.add_handler(TimerEventHandler())
