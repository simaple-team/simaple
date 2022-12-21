from typing import Optional

from simaple.app.domain.history import History, HistoryRepository
from simaple.app.domain.simulator import Simulator, SimulatorRepository


class InmemorySimulatorRepository(SimulatorRepository):
    def __init__(self):
        self._workspaces: dict[str, Simulator] = {}

    def add(self, simulator: Simulator) -> None:
        self._workspaces[simulator.id] = simulator

    def update(self, simulator: Simulator) -> None:
        self._workspaces[simulator.id] = simulator

    def get(self, simulator_id: str) -> Optional[Simulator]:
        return self._workspaces.get(simulator_id)

    def get_all(self) -> list[Simulator]:
        return list(self._workspaces.values())


class InmemoryHistoryRepository(HistoryRepository):
    def __init__(self):
        self._histories: dict[str, History] = {}

    def add(self, history: History) -> None:
        self._histories[history.id] = history

    def update(self, history: History) -> None:
        self._histories[history.id] = history

    def get(self, history_id: str) -> Optional[History]:
        return self._histories.get(history_id)
