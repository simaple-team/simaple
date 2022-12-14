from typing import Optional

from simaple.app.domain.history import History, HistoryRepository
from simaple.app.domain.workspace import Workspace, WorkspaceRepository


class InmemoryWorkspaceRepository(WorkspaceRepository):
    def __init__(self):
        self._workspaces: dict[str, Workspace] = {}

    def add(self, workspace: Workspace) -> None:
        self._workspaces[workspace.id] = workspace

    def update(self, workspace: Workspace) -> None:
        self._workspaces[workspace.id] = workspace

    def get(self, workspace_id: str) -> Optional[Workspace]:
        return self._workspaces.get(workspace_id)


class InmemoryHistoryRepository(HistoryRepository):
    def __init__(self):
        self._histories: dict[str, History] = {}

    def add(self, history: History) -> None:
        self._histories[history.id] = history

    def update(self, history: History) -> None:
        self._histories[history.id] = history

    def get(self, history_id: str) -> Optional[History]:
        return self._histories.get(history_id)
