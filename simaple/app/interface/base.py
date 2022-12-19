from simaple.app.infrastructure.repository import (
    InmemoryHistoryRepository,
    InmemorySimulatorRepository,
)
from simaple.app.infrastructure.uow import SimpleUnitOfWork

_simulator_repository = InmemorySimulatorRepository()
_history_repository = InmemoryHistoryRepository()

_unit_of_work = SimpleUnitOfWork(
    _history_repository,
    _simulator_repository,
)


def get_simulator_repository():
    return _simulator_repository


def get_history_repository():
    return _history_repository


def get_unit_of_work():
    return _unit_of_work
