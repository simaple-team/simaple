from __future__ import annotations

import abc
import uuid
from datetime import datetime
from typing import Optional

import pydantic

from simaple.app.domain.simulator import Simulator
from simaple.simulate.interface.simulator_configuration import SimulatorConfiguration


def get_uuid() -> str:
    return str(uuid.uuid4())


class Snapshot(pydantic.BaseModel, arbitrary_types_allowed=True):
    id: str = pydantic.Field(default_factory=get_uuid)
    saved_history: dict
    updated_at: datetime
    name: str
    configuration: SimulatorConfiguration

    def restore_simulator(self) -> Simulator:
        simulator = Simulator.create_from_config(self.configuration)
        simulator.engine.load_history(self.saved_history)

        return simulator

    @classmethod
    def create_from_simluator(cls, name: str, simulator: Simulator):
        return Snapshot(
            saved_history=simulator.engine.save_history(),
            updated_at=datetime.now(),
            name=name,
            configuration=simulator.conf.model_copy(),
        )


class SnapshotRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def insert(self, snapshot: Snapshot) -> None: ...

    @abc.abstractmethod
    def get(self, snapshot_id: str) -> Optional[Snapshot]: ...

    @abc.abstractmethod
    def get_by_name(self, name: str) -> Optional[Snapshot]: ...

    @abc.abstractmethod
    def get_all(self) -> list[Snapshot]: ...
