from simaple.app.domain.history import HistoryRepository
from simaple.app.domain.uow import UnitOfWork
from simaple.app.domain.workspace import WorkspaceRepository


class SimpleUnitOfWork(UnitOfWork):
    def __init__(
        self,
        history_repository: HistoryRepository,
        workspace_repository: WorkspaceRepository,
    ):
        self._history_repository = history_repository
        self._workspace_repository = workspace_repository

    def history_repository(self) -> HistoryRepository:
        return self._history_repository

    def workspace_repository(self) -> WorkspaceRepository:
        return self._workspace_repository
