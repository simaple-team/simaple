from typing import Optional

from simaple.app.domain.simulator import Simulator, SimulatorRepository


class InmemorySimulatorRepository(SimulatorRepository):
    def __init__(self) -> None:
        self._workspaces: dict[str, Simulator] = {}

    def add(self, simulator: Simulator) -> None:
        self._workspaces[simulator.id] = simulator

    def update(self, simulator: Simulator) -> None:
        self._workspaces[simulator.id] = simulator

    def get(self, simulator_id: str) -> Optional[Simulator]:
        return self._workspaces.get(simulator_id)

    def get_all(self) -> list[Simulator]:
        return list(self._workspaces.values())
