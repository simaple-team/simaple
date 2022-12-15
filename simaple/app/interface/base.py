from simaple.app.infrastructure.repository import (
    InmemoryHistoryRepository,
    InmemoryWorkspaceRepository,
)
from simaple.app.infrastructure.uow import SimpleUnitOfWork

_workspace_repository = InmemoryWorkspaceRepository()
_history_repository = InmemoryHistoryRepository()

_unit_of_work = SimpleUnitOfWork(
    _history_repository,
    _workspace_repository,
)


def get_workspace_repository():
    return _workspace_repository


def get_history_repository():
    return _history_repository


def get_unit_of_work():
    return _unit_of_work
