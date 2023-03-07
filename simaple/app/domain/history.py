import abc
import hashlib
import json
from typing import Optional

import pydantic

from simaple.core.base import Stat
from simaple.simulate.base import Action, Event, EventCallback
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.report.base import Report
from simaple.simulate.report.dpm import DamageCalculator
from simaple.simulate.reserved_names import Tag


class SimulationView(pydantic.BaseModel):
    validity_view: dict[str, Validity]
    running_view: dict[str, Running]
    buff_view: Stat

    def get_buff(self) -> Stat:
        return self.buff_view


class PlayLog(pydantic.BaseModel):
    clock: float

    action: Action
    events: list[Event]
    view: SimulationView
    checkpoint: dict[str, dict]
    checkpoint_callback: list[EventCallback]
    previous_hash: str

    @property
    def hash(self) -> str:
        stringified = self.previous_hash + json.dumps(self.dict(), sort_keys=True)
        return hashlib.sha1(stringified.encode()).hexdigest()

    def get_delay(self) -> float:
        delay = 0
        for event in self.events:
            if event.tag in (Tag.DELAY,):
                if event.payload["time"] > 0:
                    delay += event.payload["time"]

        return delay

    def get_total_damage(self, calc: DamageCalculator) -> float:
        return sum([v[1] for v in self.get_damages(calc)])

    def get_damages(self, calc: DamageCalculator) -> list[tuple[str, float]]:
        report = self.create_report()

        return [(damage_log.name, calc.get_damage(damage_log)) for damage_log in report]

    def create_report(self) -> Report:
        report = Report()
        for event in self.events:
            if event.tag == Tag.DAMAGE:
                report.add(0, event, self.view.get_buff())

        return report


class History(pydantic.BaseModel):
    id: str
    logs: list[PlayLog]

    def get(self, idx: int) -> PlayLog:
        return self.logs[idx]

    def get_latest_playlog(self) -> PlayLog:
        return self.logs[-1]

    def append(self, playlog: PlayLog) -> None:
        self.logs.append(playlog)

    def get_hash_index(self, log_hash: str) -> int:
        for idx, log in enumerate(self.logs[1:]):
            if log.previous_hash == log_hash:
                return idx

        if self.logs[-1].hash == log_hash:
            return len(self.logs)

        raise ValueError("No matching hash")

    def __len__(self) -> int:
        return len(self.logs)

    def __iter__(self):
        return iter(self.logs)


class HistoryRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add(self, history: History) -> None:
        ...

    @abc.abstractmethod
    def get(self, history_id: str) -> Optional[History]:
        ...

    @abc.abstractmethod
    def update(self, history: History) -> None:
        ...
