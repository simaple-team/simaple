from simaple.app.domain.history import HistoryRepository
from simaple.app.domain.simulator import SimulatorRepository
from simaple.app.domain.uow import UnitOfWork


class SimpleUnitOfWork(UnitOfWork):
    def __init__(
        self,
        history_repository: HistoryRepository,
        simulator_repository: SimulatorRepository,
    ):
        self._history_repository = history_repository
        self._simulator_repository = simulator_repository

    def history_repository(self) -> HistoryRepository:
        return self._history_repository

    def simulator_repository(self) -> SimulatorRepository:
        return self._simulator_repository
