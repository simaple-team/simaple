import abc

from simaple.app.domain.history import HistoryRepository
from simaple.app.domain.simulator import SimulatorRepository


class UnitOfWork(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def history_repository(self) -> HistoryRepository:
        ...

    @abc.abstractmethod
    def simulator_repository(self) -> SimulatorRepository:
        ...
