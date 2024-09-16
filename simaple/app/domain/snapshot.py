from __future__ import annotations

import abc
import uuid
from datetime import datetime
from typing import Any, Optional

import pydantic

from simaple.app.domain.simulator import Simulator
from simaple.container.character_provider import get_character_provider
from simaple.container.simulation import CharacterProvider, SimulationSetting


def get_uuid() -> str:
    return str(uuid.uuid4())


class PlanMetadata(pydantic.BaseModel):
    configuration_name: str
    author: str = ""
    data: dict[str, Any]
    simulation_setting: SimulationSetting

    def get_character_provider_config(self) -> CharacterProvider:
        return get_character_provider(self.configuration_name, self.data)

    def load_simulator(self) -> Simulator:
        return Simulator.create_from_config(
            simulation_setting=self.simulation_setting,
            character_provider=self.get_character_provider_config(),
        )


class Snapshot(pydantic.BaseModel, arbitrary_types_allowed=True):
    id: str = pydantic.Field(default_factory=get_uuid)
    saved_history: dict
    updated_at: datetime
    name: str
    configuration: PlanMetadata

    def restore_simulator(self) -> Simulator:
        simulator = self.configuration.load_simulator()
        simulator.engine.load_history(self.saved_history)

        return simulator

    @classmethod
    def create_from_simluator(cls, name: str, simulator: Simulator):
        return Snapshot(
            saved_history=simulator.engine.save_history(),
            updated_at=datetime.now(),
            name=name,
            configuration=PlanMetadata(
                configuration_name=simulator.character_provider.get_name(),
                author="",
                data=simulator.character_provider.model_dump(),
                simulation_setting=simulator.simulation_setting,
            ),
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
