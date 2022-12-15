from simaple.simulate.base import Event
from simaple.simulate.reserved_names import Tag


def count_damage_skill(events: list[Event]) -> int:
    return sum([e.tag == Tag.DAMAGE for e in events])


def is_rejected(events: list[Event]) -> bool:
    return events[0].tag == Tag.REJECT
