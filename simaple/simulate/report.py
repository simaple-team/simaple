from simaple.simulate.base import Environment, Event, EventHandler
from simaple.simulate.reserved_names import Tag


class Report:
    def __init__(self):
        self._logs = []

    def add(self, clock, event, buff):
        self._logs.append(
            (
                clock,
                event.name,
                event.payload["damage"],
                event.payload["hit"],
                buff.short_dict(),
            )
        )

    def save(self, file_name):
        with open(file_name, "w", encoding="utf8") as f:
            for clock, name, damage, hit, buff in self._logs:
                f.write(f"{clock}\t{name}\t{damage:.3f}\t{hit}\t{buff}\n")

    def show(self):
        for clock, name, damage, hit, buff in self._logs:
            print(f"{clock}ms\t\t{name}\t{damage:.3f}\t{hit}\t{buff}")


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
