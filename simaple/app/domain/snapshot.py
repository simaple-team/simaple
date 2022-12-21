from __future__ import annotations

from simaple.app.domain.simulator import Simulator
from simaple.app.domain.history import History
from simaple.app.domain.simulator_configuration import SimulatorConfiguration

from datetime import datetime
import pydantic
import uuid
import abc

from typing import Optional

def get_uuid() -> str:
    return str(uuid.uuid4())


class Snapshot(pydantic.BaseModel):
    id: str = pydantic.Field(default_factory=get_uuid)
    history: History
    updated_at: datetime
    name: str
    configuration: SimulatorConfiguration

    def restore_simulator(self) -> Simulator:
        simulator = Simulator.create_from_config(self.configuration)
        simulator.history = self.history

        return simulator

    @classmethod
    def create_from_simluator(cls, name: str, simulator: Simulator):
        return Snapshot(
            history=simulator.history.copy(),
            updated_at=datetime.now(),
            name=name,
            configuration=simulator.conf.copy(),
        )


class SnapshotRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def insert(self, snapshot: Snapshot) -> None:
        ...

    @abc.abstractmethod
    def get(self, snapshot_id: str) -> Optional[Snapshot]:
        ...

    @abc.abstractmethod
    def get_by_name(self, name: str) -> Optional[Snapshot]:
        ...
