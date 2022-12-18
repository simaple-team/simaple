from simaple.simulate.base import Event
from simaple.simulate.reserved_names import Tag


def is_rejected(events: list[Event]) -> bool:
    return any(event.tag == Tag.REJECT for event in events)
