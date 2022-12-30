from abc import ABCMeta
from contextlib import contextmanager
from typing import Optional

import pydantic

from simaple.simulate.base import Action, Environment, Event
from simaple.simulate.component.view import KeydownView, Running, Validity
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


class DefaultMDCActor(pydantic.BaseModel, Actor):
    order: list[str]

    def decide(
        self,
        environment: Environment,
        events: list[Event],
    ) -> Action:
        validities: list[Validity] = environment.show("validity")
        runnings: list[Running] = environment.show("running")

        validity_map = {v.name: v for v in validities if v.valid}
        running_map = {r.name: r.time_left for r in runnings}
        keydown_running_name = self._get_keydown_running_name(environment)
        elapse_time = self._get_next_elapse_time(events)

        chosen_action: Optional[Action] = None

        if keydown_running_name is not None:
            chosen_action = self._decide_during_keydown(
                validity_map,
                running_map,
                keydown_running_name,
                elapse_time,
            )
        else:
            chosen_action = self._decide_default(
                validity_map,
                running_map,
                elapse_time,
            )

        if chosen_action:
            return chosen_action

        raise ValueError(
            "No valid element exist! Maybe unintended component was built?"
        )

    def _decide_during_keydown(
        self,
        validity_map: dict[str, Validity],
        running_map: dict[str, float],
        keydown_running_name: str,
        elapse_time: float,
    ):
        for name in self.order:
            if name == keydown_running_name:
                break

            if validity_map.get(name):
                if running_map.get(name, 0) > 0:
                    continue

                return Action(name=keydown_running_name, method="stop")

        return time_elapsing_action(elapse_time)

    def _decide_default(
        self,
        validity_map: dict[str, Validity],
        running_map: dict[str, float],
        elapse_time: float,
    ):
        if elapse_time > 0:
            return time_elapsing_action(elapse_time)

        for name in self.order:
            if validity_map.get(name):
                if running_map.get(name, 0) > 0:
                    continue

                return Action(name=name, method="use")

        for v in validity_map.values():
            if v.valid:
                return Action(name=v.name, method="use")

        return None

    def _get_keydown_running_name(self, environment: Environment) -> Optional[str]:
        keydowns: list[KeydownView] = environment.show("keydown")
        keydown_running_list = [k.name for k in keydowns if k.running]

        return next(iter(keydown_running_list), None)

    def _get_next_elapse_time(self, events: list[Event]) -> float:
        for event in events:
            if event.tag in (Tag.DELAY,) and event.payload["time"] > 0:
                return event.payload["time"]  # type: ignore

        return 0.0
