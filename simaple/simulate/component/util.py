from functools import wraps

from simaple.simulate.base import Event
from simaple.simulate.reserved_names import Tag


def is_rejected(events: list[Event]) -> bool:
    return any(event["tag"] == Tag.REJECT for event in events)


def is_keydown_ended(events: list[Event]) -> bool:
    return any(event["tag"] == Tag.KEYDOWN_END for event in events)


def ignore_rejected(func):
    """
    Ignores rejected events from action.
    This method is used for actions which yields "intened" rejection.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        state, events = func(*args, **kwargs)
        return state, [event for event in events if event["tag"] != Tag.REJECT]

    return wrapper
