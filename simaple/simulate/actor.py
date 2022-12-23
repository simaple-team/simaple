from abc import ABCMeta
from contextlib import contextmanager

import pydantic

from simaple.simulate.base import Action, Environment, Event
from simaple.simulate.reserved_names import Tag


class ActionRecorder:
    def __init__(self, file_name):
        self._file_name = file_name
        self._fp = None

    @contextmanager
    def start(self):
        with open(self._file_name, "w", encoding="utf-8") as fp:
            self._fp = fp
            yield self

    def write(self, action: Action, timestamp: float):
        self._fp.write(f"{timestamp}\t{action.json(ensure_ascii=False)}\n")


def time_elapsing_action(time: float) -> Action:
    return Action(name="*", method="elapse", payload=time)


class Actor(metaclass=ABCMeta):
    def decide(self, environment: Environment, events: list[Event]) -> Action:
        ...


class AlwaysDelayedActor(Actor):
    def decide(self, environment: Environment, events: list[Event]) -> Action:
        for event in events:
            if event.payload is None:
                raise ValueError
            if event.tag in (Tag.DELAY,) and event.payload["time"] > 0:
                return time_elapsing_action(event.payload["time"])

        return self._decide(environment, events)

    def _decide(self, environment: Environment, events: list[Event]) -> Action:
        ...


class DefaultMDCActor(pydantic.BaseModel, AlwaysDelayedActor):
    order: list[str]

    def _decide(self, environment: Environment, events: list[Event]) -> Action:
        validities = environment.show("validity")
        runnings = environment.show("running")

        validity_map = {v.name: v for v in validities if v.valid}
        running_map = {d.name: d.time_left for d in runnings}

        for name in self.order:
            if validity_map.get(name):
                if running_map.get(name, 0) > 0:
                    continue

                return Action(
                    name=name,
                    method="use",
                )

        for v in validities:
            if v.valid:
                return Action(
                    name=v.name,
                    method="use",
                )

        raise ValueError("No valid element exist! Maybe wrong component build?")
