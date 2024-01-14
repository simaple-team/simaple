import pydantic

from simaple.core.base import Stat
from simaple.simulate.base import Event


class DamageLog(pydantic.BaseModel):
    clock: float
    name: str
    damage: float
    hit: float
    buff: Stat
    tag: str

    def serialize(self):
        return f"{self.clock}\t{self.name}\t{self.tag}\t{self.damage:.3f}\t{self.hit}\t{self.buff.short_dict()}"


class Report(pydantic.BaseModel):
    logs: list[DamageLog] = []

    def add(self, clock: float, event: Event, buff: Stat):
        buff_stat = buff
        if event["payload"]["damage"] != 0 and event["payload"]["hit"] != 0:
            if event["payload"].get("modifier") is not None:
                buff_stat = buff_stat + Stat.model_validate(
                    event["payload"]["modifier"]
                )

            self.logs.append(
                DamageLog(
                    clock=clock,
                    name=event["name"],
                    damage=event["payload"]["damage"],
                    hit=event["payload"]["hit"],
                    buff=buff_stat,
                    tag=event["tag"] or "",
                )
            )

    def extend(self, report: "Report"):
        self.logs.extend(report.logs)

    def save(self, file_name: str):
        with open(file_name, "w", encoding="utf8") as f:
            for log in self.logs:
                f.write(log.serialize() + "\n")

    def total_time(self):
        return self.logs[-1].clock
