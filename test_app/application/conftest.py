from typing import Optional

import pytest

from simaple.app.domain.simulator import SimulatorRepository
from simaple.app.domain.simulator_configuration import MinimalSimulatorConfiguration
from simaple.app.domain.snapshot import Snapshot, SnapshotRepository
from simaple.app.domain.uow import UnitOfWork
from simaple.app.infrastructure.component_schema_repository import (
    LoadableComponentSchemaRepository,
)
from simaple.app.infrastructure.repository import InmemorySimulatorRepository
from simaple.spec.repository import DirectorySpecRepository
from simaple.data.skill import get_kms_spec_resource_path


class InmemorySnapshotRepository(SnapshotRepository):
    def __init__(self):
        self._db: dict[str, Snapshot] = {}

    def insert(self, snapshot: Snapshot) -> None:
        self._db[snapshot.id] = snapshot

    def get_all(self) -> list[Snapshot]:
        return list(self._db.values())

    def get(self, snapshot_id: str) -> Optional[Snapshot]:
        return self._db.get(snapshot_id)

    def get_by_name(self, name: str) -> Optional[Snapshot]:
        for el in self._db.values():
            if el.name == name:
                return el

        return None


class InmemoryUnitOfWork(UnitOfWork):
    def __init__(self):
        self._snapshot_repository: InmemorySnapshotRepository = (
            InmemorySnapshotRepository()
        )
        self._simulator_repository: InmemorySimulatorRepository = (
            InmemorySimulatorRepository()
        )
        self._component_schema_repository: LoadableComponentSchemaRepository = (
            LoadableComponentSchemaRepository()
        )
        self._spec_repository: DirectorySpecRepository = (
            DirectorySpecRepository(get_kms_spec_resource_path())
        )

    def snapshot_repository(self) -> SnapshotRepository:
        return self._snapshot_repository

    def simulator_repository(self) -> SimulatorRepository:
        return self._simulator_repository

    def component_schema_repository(self) -> LoadableComponentSchemaRepository:
        return self._component_schema_repository

    def spec_repository(self) -> DirectorySpecRepository:
        return self._spec_repository

    def commit(self) -> None:
        return


@pytest.fixture
def uow():
    return InmemoryUnitOfWork()


@pytest.fixture
def minimal_conf(simulator_configuration):
    return MinimalSimulatorConfiguration.model_validate(simulator_configuration)
