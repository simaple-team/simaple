import pydantic

from simaple.core.base import Stat
from simaple.simulate.base import Environment, Event, EventHandler
from simaple.simulate.reserved_names import Tag


class DamageLog(pydantic.BaseModel):
    clock: float
    name: str
    damage: float
    hit: float
    buff: Stat

    def __str__(self):
        return f"{self.clock}ms\t\t{self.name}\t{self.damage:.3f}\t{self.hit}\t{self.buff.short_dict()}"

    def serialize(self):
        return f"{self.clock}\t{self.name}\t{self.damage:.3f}\t{self.hit}\t{self.buff.short_dict()}"


class Report:
    def __init__(self):
        self._logs: list[DamageLog] = []

    def __iter__(self):
        return iter(self._logs)

    def add(self, clock, event, buff):
        buff_stat = buff
        if event.payload["damage"] != 0 and event.payload["hit"] != 0:
            if event.payload["modifier"] is not None:
                buff_stat = buff_stat + event.payload["modifier"]

            self._logs.append(
                DamageLog(
                    clock=clock,
                    name=event.name,
                    damage=event.payload["damage"],
                    hit=event.payload["hit"],
                    buff=buff_stat.short_dict(),
                )
            )

    def save(self, file_name):
        with open(file_name, "w", encoding="utf8") as f:
            for log in self._logs:
                f.write(log.serialize() + "\n")

    def show(self):
        for log in self._logs:
            print(log)

    def total_time(self):
        return self._logs[-1].clock


class ReportEventHandler(EventHandler):
    def __init__(self, report: Report):
        self.report = report

    def __call__(
        self, event: Event, environment: Environment, all_events: list[Event]
    ) -> None:
        if event.tag == Tag.DAMAGE:
            current_buff_state = environment.show("buff")
            current_clock = environment.show("clock")
            self.report.add(current_clock, event, current_buff_state)
