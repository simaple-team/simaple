from __future__ import annotations

import abc
import uuid
from typing import Optional

import pydantic

from simaple.app.domain.history import History, PlayLog, SimulationView
from simaple.app.domain.simulator_configuration import SimulatorConfiguration
from simaple.simulate.base import Action, Client
from simaple.simulate.report.dpm import DPMCalculator


class Simulator(pydantic.BaseModel):
    id: str
    client: Client
    calculator: DPMCalculator
    conf: SimulatorConfiguration  # polymorphic

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def create_from_config(cls, conf: SimulatorConfiguration) -> Simulator:
        return Simulator(
            id=str(uuid.uuid4()),
            client=conf.create_client(),
            calculator=conf.create_damage_calculator(),
            conf=conf,
        )

    def empty_action_playlog(self) -> PlayLog:
        return PlayLog(
            events=[],
            view=self.get_simulation_view(),
            clock=self.client.environment.show("clock"),
            action=Action(name="*", method="elapse", payload=0),
            checkpoint=self.client.environment.store.save(),
        )

    def get_simulation_view(self) -> SimulationView:
        return SimulationView(
            validity_view={v.name: v for v in self.client.environment.show("validity")},
            running_view={v.name: v for v in self.client.environment.show("running")},
            buff_view=self.client.environment.show("buff"),
        )

    def dispatch(self, action: Action) -> PlayLog:
        events = self.client.play(action)

        return PlayLog(
            clock=self.client.environment.show("clock"),
            view=self.get_simulation_view(),
            action=action,
            events=events,
            checkpoint=self.client.environment.store.save(),
        )


class SimulatorRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add(self, simulator: Simulator) -> None:
        ...

    @abc.abstractmethod
    def get(self, simulator_id: str) -> Optional[Simulator]:
        ...

    @abc.abstractmethod
    def update(self, simulator: Simulator) -> None:
        ...
