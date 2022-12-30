from simaple.simulate.base import Event
from simaple.simulate.reserved_names import Tag


def is_rejected(events: list[Event]) -> bool:
    return any(event.tag == Tag.REJECT for event in events)


def is_keydown_ended(events: list[Event]) -> bool:
    return any(event.tag == Tag.KEYDOWN_END for event in events)
