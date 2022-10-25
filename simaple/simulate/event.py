from simaple.simulate.base import Event


def rejected_event(name: str):
    return Event(name=name, tag="global.reject")


def elapsed_event(name: str, time: float):
    return Event(name=name, tag="global.elapsed", payload={"time": time})


def action_delay_triggered(name: str, time: float):
    return Event(name=name, tag="global.delay", payload={"time": time})


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
