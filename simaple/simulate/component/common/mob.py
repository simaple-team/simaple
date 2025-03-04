from typing import TypedDict

import pydantic

from simaple.simulate.component.base import Component, reducer_method
from simaple.simulate.core.base import Entity, Event
from simaple.simulate.reserved_names import Tag


class DOT(Entity):
    current: dict[str, tuple[float, float]] = pydantic.Field(
        default_factory=dict
    )  # name, damage, lasting_time
    period_time_left: float = 1_000.0
    period: float = 1_000.0

    def new(self, name: str, damage: float, lasting_time: float) -> None:
        self.current[name] = (damage, lasting_time)

    def elapse(self, time: float) -> dict[tuple[str, float], int]:
        emits: dict[tuple[str, float], int] = {}  # (name, damage): count

        elapse_time_left = time
        while elapse_time_left > 0:
            elapse_time_left, events = self.step(elapse_time_left)
            for k in events:
                emits[k] = emits.get(k, 0) + 1

        return emits

    def step(self, time: float) -> tuple[float, list[tuple[str, float]]]:
        if self.period_time_left > time:
            self.period_time_left -= time
            return 0, []

        left_time = time - self.period_time_left
        lapse_time = self.period_time_left

        new_current = {
            name: (damage, lasting_time - lapse_time)
            for name, (damage, lasting_time) in self.current.items()
            if lasting_time - lapse_time >= 0
        }
        events = [(name, damage) for name, (damage, _) in new_current.items()]

        self.current = new_current
        self.period_time_left = self.period

        return left_time, events


class MobState(TypedDict):
    dot: DOT


class DOTRequestPayload(pydantic.BaseModel):
    name: str
    damage: float
    lasting_time: float


class MobComponent(Component):
    def get_default_state(self) -> MobState:
        return {"dot": DOT(current={})}

    @reducer_method
    def add_dot(self, payload: DOTRequestPayload, state: MobState):
        dot = state["dot"]

        dot.new(payload.name, payload.damage, payload.lasting_time)
        state["dot"] = dot

        return state, []

    @reducer_method
    def elapse(self, time: float, state: MobState):
        dot = state["dot"]

        emits = dot.elapse(time)

        events: list[Event] = [
            {
                "name": name,
                "tag": Tag.DOT,
                "payload": {"damage": damage, "hit": hit},
                "method": "elapse",
                "handler": None,
            }
            for ((name, damage), hit) in emits.items()
        ]
        state["dot"] = dot

        return state, events
