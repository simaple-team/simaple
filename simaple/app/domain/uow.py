import abc

from simaple.app.domain.component_schema import ComponentSchemaRepository
from simaple.app.domain.simulator import SimulatorRepository
from simaple.app.domain.snapshot import SnapshotRepository


class UnitOfWork(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def snapshot_repository(self) -> SnapshotRepository:
        ...

    @abc.abstractmethod
    def simulator_repository(self) -> SimulatorRepository:
        ...

    @abc.abstractmethod
    def component_schema_repository(self) -> ComponentSchemaRepository:
        ...

    @abc.abstractmethod
    def commit(self) -> None:
        ...
