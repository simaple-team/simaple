from simaple.simulate.base import Event


def damage_event(name: str, damage: float, hit: float, delay: float):
    return Event(
        name=name,
        tag="global.damage",
        payload={
            "damage": damage,
            "hit": hit,
            "delay": delay,
        },
    )


def buff_used_event():
    return Event(
        tag="global.buff.used",
    )


def interval_damage_event(name: str, damage: float, hit: float, count: int):
    return Event(
        name=name,
        tag="global.damage.interval",
        payload={
            "damage": damage,
            "hit": hit,
            "count": count,
        },
    )
