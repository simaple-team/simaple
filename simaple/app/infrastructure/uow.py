from typing import Callable

from sqlalchemy.orm import Session

from simaple.app.domain.simulator import SimulatorRepository
from simaple.app.domain.uow import UnitOfWork
from simaple.app.infrastructure.component_schema_repository import (
    LoadableComponentSchemaRepository,
)
from simaple.app.infrastructure.snapshot_repository import SqlSnapshotRepository
from simaple.spec.repository import SpecRepository


class SimpleUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session_builder: Callable[[], Session],
        simulator_repository: SimulatorRepository,
        component_schema_repository: LoadableComponentSchemaRepository,
        spec_repository: SpecRepository,
    ):
        self._session = session_builder()
        self._simulator_repository = simulator_repository
        self._component_schema_repository = component_schema_repository
        self._spec_repository = spec_repository

    def snapshot_repository(self) -> SqlSnapshotRepository:
        return SqlSnapshotRepository(self._session)

    def simulator_repository(self) -> SimulatorRepository:
        return self._simulator_repository

    def component_schema_repository(self) -> LoadableComponentSchemaRepository:
        return self._component_schema_repository

    def commit(self) -> None:
        self._session.commit()

    def spec_repository(self) -> SpecRepository:
        return self._spec_repository
