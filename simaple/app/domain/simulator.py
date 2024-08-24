from __future__ import annotations

import abc
import uuid
from typing import Optional

import pydantic

from simaple.simulate.engine import OperationEngine
from simaple.simulate.interface.simulator_configuration import SimulatorConfiguration
from simaple.simulate.policy.base import Operation
from simaple.simulate.policy.parser import parse_dsl_to_operations
from simaple.simulate.report.dpm import DamageCalculator


class Simulator(pydantic.BaseModel):
    # TODO: Taint?
    id: str
    engine: OperationEngine
    calculator: DamageCalculator
    conf: SimulatorConfiguration  # polymorphic

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def create_from_config(cls, conf: SimulatorConfiguration) -> Simulator:
        simulator_id = str(uuid.uuid4())
        simulation = Simulator(
            id=simulator_id,
            engine=conf.create_operation_engine(),
            calculator=conf.create_damage_calculator(),
            conf=conf,
        )
        return simulation

    def get_valid_skill_names(self) -> list[str]:
        validity_view = self.engine.get_current_viewer()("validitiy")
        return list(view.name for view in validity_view)

    def dispatch(self, dsl: str) -> None:
        for op in parse_dsl_to_operations(dsl):
            self.engine.exec(op)

    def exec(self, op: Operation) -> None:
        self.engine.exec(op)

    def rollback_by_hash(self, log_hash: str) -> None:
        index = self.engine.history().get_hash_index(log_hash)
        self.engine.rollback(index)

    def rollback(self, history_index: int) -> None:
        """
        Rollback into history {history_index}.
        This operator maintains history until {history_index} and discards the rest.
        Be careful that history at "history_index" is not discarded.
        """
        self.engine.rollback(history_index)

    def set_history(self, saved_history: dict) -> None:
        self.engine.load_history(saved_history)


class SimulatorRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add(self, simulator: Simulator) -> None: ...

    @abc.abstractmethod
    def get(self, simulator_id: str) -> Optional[Simulator]: ...

    @abc.abstractmethod
    def get_all(self) -> list[Simulator]: ...

    @abc.abstractmethod
    def update(self, simulator: Simulator) -> None: ...
