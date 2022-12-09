from simaple.simulate.base import Event
from simaple.simulate.reserved_names import Tag


def count_damage_skill(events: list[Event]) -> int:
    return sum([e.tag == Tag.DAMAGE for e in events])
