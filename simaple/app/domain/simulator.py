from __future__ import annotations

import abc
import uuid
from typing import Optional

import pydantic

from simaple.app.domain.history import History, PlayLog, SimulationView
from simaple.app.domain.simulator_configuration import SimulatorConfiguration
from simaple.simulate.base import Action, Client
from simaple.simulate.report.dpm import DamageCalculator


class Simulator(pydantic.BaseModel):
    id: str
    client: Client
    calculator: DamageCalculator
    conf: SimulatorConfiguration  # polymorphic
    history: History

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def create_from_config(cls, conf: SimulatorConfiguration) -> Simulator:
        simulator_id = str(uuid.uuid4())
        simulation = Simulator(
            id=simulator_id,
            client=conf.create_client(),
            calculator=conf.create_damage_calculator(),
            conf=conf,
            history=History(id=simulator_id, logs=[]),
        )
        simulation.add_empty_action_playlog()
        return simulation

    def add_empty_action_playlog(self) -> None:
        self.history.append(
            PlayLog(
                events=[],
                view=self.get_simulation_view(),
                clock=self.client.environment.show("clock"),
                action=Action(name="*", method="elapse", payload=0),
                checkpoint=self.client.environment.store.save(),
                checkpoint_callback=[],
            )
        )

    def get_simulation_view(self) -> SimulationView:
        return SimulationView(
            validity_view={v.name: v for v in self.client.environment.show("validity")},
            running_view={v.name: v for v in self.client.environment.show("running")},
            buff_view=self.client.environment.show("buff"),
        )

    def dispatch(self, action: Action) -> None:
        events = self.client.play(action)

        playlog = PlayLog(
            clock=self.client.environment.show("clock"),
            view=self.get_simulation_view(),
            action=action,
            events=events,
            checkpoint=self.client.environment.store.save(),
            checkpoint_callback=self.client.export_previous_callbacks(),
        )

        self.history.append(playlog)

    def rollback(self, history_index: int) -> None:
        self.history.logs = self.history.logs[: history_index + 1]
        last_playlog = self.history.logs[-1]
        self.client.environment.store.load(last_playlog.checkpoint)
        self.client.restore_previous_callbacks(last_playlog.checkpoint_callback)

    def set_history(self, history: History) -> None:
        self.history = history
        self.rollback(len(history) - 1)

    def change_current_checkpoint(self, ckpt: dict) -> None:
        last_playlog = self.history.logs[-1].copy()
        last_playlog.checkpoint = ckpt
        self.history.logs[-1] = last_playlog

        self.client.environment.store.load(last_playlog.checkpoint)
        self.client.restore_previous_callbacks(last_playlog.checkpoint_callback)


class SimulatorRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add(self, simulator: Simulator) -> None:
        ...

    @abc.abstractmethod
    def get(self, simulator_id: str) -> Optional[Simulator]:
        ...

    @abc.abstractmethod
    def get_all(self) -> list[Simulator]:
        ...

    @abc.abstractmethod
    def update(self, simulator: Simulator) -> None:
        ...
