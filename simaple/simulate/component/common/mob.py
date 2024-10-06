import pydantic

from simaple.simulate.base import Entity
from simaple.simulate.component.base import Component, ReducerState, reducer_method
from simaple.simulate.reserved_names import Tag


class DOT(Entity):
    current: dict[str, tuple[float, float]] = pydantic.Field(
        default_factory=dict
    )  # name, damage, lasting_time
    period_time_left: float = 1_000.0
    period: float = 1_000.0

    def new(self, name: str, damage: float, lasting_time: float):
        current = self.current.copy()
        current[name] = (damage, lasting_time)
        return self.model_copy(
            update={
                "current": current,
            }
        )

    def elapse(self, time: float):
        emits: dict[tuple[str, float], int] = {}  # (name, damage): count
        period_time_left = self.period_time_left - time
        current = self.current

        while period_time_left <= 0:
            period_time_left += self.period
            for name, (damage, _) in current.items():
                emits[(name, damage)] = emits.get((name, damage), 0) + 1

            current = {
                name: (damage, lasting_time - self.period)
                for name, (damage, lasting_time) in current.items()
                if lasting_time - self.period > 0
            }

        return (
            self.model_copy(
                update={
                    "current": current,
                    "period_time_left": period_time_left,
                },
            ),
            emits,
        )


class MobState(ReducerState):
    dot: DOT


class DOTRequestPayload(pydantic.BaseModel):
    name: str
    damage: float
    lasting_time: float


class MobComponent(Component):
    def get_default_state(self) -> dict[str, Entity]:
        return {"dot": DOT(current={})}

    @reducer_method
    def add_dot(self, payload: DOTRequestPayload, state: MobState):
        return state.copy(
            {"dot": state.dot.new(payload.name, payload.damage, payload.lasting_time)}
        ), []

    @reducer_method
    def elapse(self, time: float, state: MobState):
        dot, emits = state.dot.elapse(time)

        events = [
            {"name": name, "tag": Tag.DOT, "payload": {"damage": damage, "hit": hit}}
            for ((name, damage), hit) in emits.items()
        ]

        return state.copy({"dot": dot}), events
