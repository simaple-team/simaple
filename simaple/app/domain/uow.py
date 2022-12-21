import abc

from simaple.app.domain.snapshot import SnapshotRepository
from simaple.app.domain.simulator import SimulatorRepository


class UnitOfWork(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def snapshot_repository(self) -> SnapshotRepository:
        ...

    @abc.abstractmethod
    def simulator_repository(self) -> SimulatorRepository:
        ...

    @abc.abstractmethod
    def commit(self) -> None:
        ...

