import pydantic

from simaple.core.base import Stat
from simaple.simulate.core import Action, Event
from simaple.simulate.core.runtime import PlayLog
from simaple.simulate.reserved_names import Tag


class DamageLog(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    name: str
    damage: float
    hit: float
    buff: Stat
    tag: str

    def __repr__(self):
        return f"{self.name}\t{self.tag}\t{self.damage:.3f}\t{self.hit}\t{self.buff.short_dict()}"


def _create_damage_log(event: Event, buff: Stat) -> DamageLog | None:
    if event["tag"] not in (Tag.DAMAGE, Tag.DOT):
        return None

    if event["payload"]["damage"] == 0 or event["payload"]["hit"] == 0:
        return None

    buff_stat = buff
    if event["payload"].get("modifier") is not None:
        buff_stat = buff_stat + Stat.model_validate(event["payload"]["modifier"])

    return DamageLog(
        name=event["name"],
        damage=event["payload"]["damage"],
        hit=event["payload"]["hit"],
        buff=buff_stat,
        tag=event["tag"] or "",
    )


class SimulationEntry(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    action: Action
    clock: float
    damage_logs: list[DamageLog]
    accepted: bool

    @classmethod
    def build(cls, playlog: PlayLog, buff: Stat) -> "SimulationEntry":
        maybe_damage_logs = [
            _create_damage_log(event, buff) for event in playlog.events
        ]
        damage_logs: list[DamageLog] = [
            damage_logs for damage_logs in maybe_damage_logs if damage_logs is not None
        ]

        return SimulationEntry(
            action=playlog.action,
            clock=playlog.clock,
            damage_logs=damage_logs,
            accepted=all([event["tag"] != Tag.REJECT for event in playlog.events]),
        )
