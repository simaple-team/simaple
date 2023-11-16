from __future__ import annotations

import abc
import uuid
from typing import Optional

import pydantic

from simaple.app.domain.simulator_configuration import SimulatorConfiguration
from simaple.simulate.policy.base import Operation, SimulationHistory
from simaple.simulate.policy.dsl import DSLShell
from simaple.simulate.report.dpm import DamageCalculator


class Simulator(pydantic.BaseModel):
    id: str
    shell: DSLShell
    calculator: DamageCalculator
    conf: SimulatorConfiguration  # polymorphic

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def create_from_config(cls, conf: SimulatorConfiguration) -> Simulator:
        simulator_id = str(uuid.uuid4())
        simulation = Simulator(
            id=simulator_id,
            shell=conf.create_shell(),
            calculator=conf.create_damage_calculator(),
            conf=conf,
        )
        return simulation

    def get_valid_skill_names(self) -> list[str]:
        validity_view = self.shell.get_viewer(self.shell.get(0).playlogs[0])(
            "validitiy"
        )
        return list(view.name for view in validity_view)

    def dispatch(self, dsl: str) -> None:
        self.shell.exec_dsl(dsl)

    def rollback_by_hash(self, log_hash: str) -> None:
        index = self.shell.get_hash_index(log_hash)
        self.shell.rollback(index)

    def rollback(self, history_index: int) -> None:
        self.shell.rollback(history_index)

    def set_history(self, saved_history: dict) -> None:
        self.shell.load_history(saved_history)


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
