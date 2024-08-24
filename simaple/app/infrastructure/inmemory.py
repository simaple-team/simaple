from typing import Optional

from simaple.app.domain.simulator import SimulatorRepository
from simaple.app.domain.snapshot import Snapshot, SnapshotRepository
from simaple.app.domain.uow import UnitOfWork
from simaple.app.infrastructure.component_schema_repository import (
    LoadableComponentSchemaRepository,
)
from simaple.spec.repository import SpecRepository


class InmemorySnapshotRepository(SnapshotRepository):
    def __init__(self) -> None:
        self._snapshots: dict[str, Snapshot] = {}

    def insert(self, snapshot: Snapshot) -> None:
        self._snapshots[snapshot.id] = snapshot

    def get_all(self) -> list[Snapshot]:
        return list(self._snapshots.values())

    def get(self, snapshot_id: str) -> Optional[Snapshot]:
        return self._snapshots.get(snapshot_id)

    def get_by_name(self, name: str) -> Optional[Snapshot]:
        for snapshot in self._snapshots.values():
            if snapshot.name == name:
                return snapshot

        return None


class SessionlessUnitOfWork(UnitOfWork):
    def __init__(
        self,
        simulator_repository: SimulatorRepository,
        component_schema_repository: LoadableComponentSchemaRepository,
        spec_repository: SpecRepository,
        snapshot_repository: SnapshotRepository,
    ):
        self._simulator_repository = simulator_repository
        self._component_schema_repository = component_schema_repository
        self._spec_repository = spec_repository
        self._snapshot_repository = snapshot_repository

    def snapshot_repository(self) -> SnapshotRepository:
        return self._snapshot_repository

    def simulator_repository(self) -> SimulatorRepository:
        return self._simulator_repository

    def component_schema_repository(self) -> LoadableComponentSchemaRepository:
        return self._component_schema_repository

    def commit(self) -> None:
        return

    def spec_repository(self) -> SpecRepository:
        return self._spec_repository
