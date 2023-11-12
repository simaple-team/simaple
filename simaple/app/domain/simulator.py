from __future__ import annotations

import abc
import uuid
from typing import Optional

import pydantic

from simaple.app.domain.history import History, PlayLog, SimulationView
from simaple.app.domain.simulator_configuration import SimulatorConfiguration
from simaple.simulate.base import Action, Checkpoint, Client
from simaple.simulate.report.dpm import DamageCalculator


class Simulator(pydantic.BaseModel):
    id: str
    client: Client
    calculator: DamageCalculator
    conf: SimulatorConfiguration  # polymorphic
    history: History

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

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

    def get_valid_skill_names(self) -> list[str]:
        validity_view = self.client.show("validitiy")
        return list(view.name for view in validity_view)

    def add_empty_action_playlog(self) -> None:
        self.history.append(
            PlayLog(
                events=[],
                view=self.get_simulation_view(),
                clock=self.client.show("clock"),
                action=dict(name="*", method="elapse", payload=0),
                checkpoint=self.client.save(),
                previous_hash="",
            )
        )

    def get_simulation_view(self) -> SimulationView:
        return SimulationView(
            validity_view={v.name: v for v in self.client.show("validity")},
            running_view={v.name: v for v in self.client.show("running")},
            buff_view=self.client.show("buff"),
        )

    def dispatch(self, action: Action) -> None:
        events = self.client.play(action)

        playlog = PlayLog(
            clock=self.client.show("clock"),
            view=self.get_simulation_view(),
            action=action,
            events=events,
            checkpoint=self.client.save(),
            previous_hash=self.history.logs[-1].hash,
        )

        self.history.append(playlog)

    def rollback_by_hash(self, log_hash: str) -> None:
        index = self.history.get_hash_index(log_hash)
        self.rollback(index)

    def rollback(self, history_index: int) -> None:
        self.history.logs = self.history.logs[: history_index + 1]
        last_playlog = self.history.logs[-1]
        self.client.load(last_playlog.checkpoint)

    def set_history(self, history: History) -> None:
        self.history = history
        self.rollback(len(history) - 1)

    def change_current_checkpoint(self, ckpt: Checkpoint) -> None:
        last_playlog = self.history.logs[-1].model_copy()
        last_playlog.checkpoint = ckpt
        self.history.logs[-1] = last_playlog
        self.client.load(last_playlog.checkpoint)


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
