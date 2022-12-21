import os
from typing import Optional

import pytest

from simaple.app.domain.simulator import SimulatorRepository
from simaple.app.domain.snapshot import Snapshot, SnapshotRepository
from simaple.app.domain.uow import UnitOfWork
from simaple.app.infrastructure.repository import InmemorySimulatorRepository


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

    def snapshot_repository(self) -> SnapshotRepository:
        return self._snapshot_repository

    def simulator_repository(self) -> SimulatorRepository:
        return self._simulator_repository

    def commit(self) -> None:
        return


@pytest.fixture
def uow():
    return InmemoryUnitOfWork()
