from simaple.app.infrastructure.snapshot_repository import SqlSnapshotRepository
from simaple.app.domain.simulator import SimulatorRepository
from simaple.app.domain.uow import UnitOfWork
from sqlalchemy.orm import Session
from typing import Callable


class SimpleUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session_builder: Callable[[], Session],
        simulator_repository: SimulatorRepository,
    ):
        self._session = session_builder()
        self._simulator_repository = simulator_repository

    def snapshot_repository(self) -> SqlSnapshotRepository:
        return SqlSnapshotRepository(self._session)

    def simulator_repository(self) -> SimulatorRepository:
        return self._simulator_repository

    def commit(self) -> None:
        self._session.commit()
