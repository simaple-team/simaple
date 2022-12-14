import abc

from simaple.app.domain.history import HistoryRepository
from simaple.app.domain.workspace import WorkspaceRepository


class UnitOfWork(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def history_repository(self) -> HistoryRepository:
        ...

    @abc.abstractmethod
    def workspace_repository(self) -> WorkspaceRepository:
        ...
