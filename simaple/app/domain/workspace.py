import abc
from typing import Optional

import pydantic

from simaple.app.domain.history import PlayLog, SimulationView
from simaple.simulate.base import Action, Client
from simaple.simulate.report.dpm import DPMCalculator


class Workspace(pydantic.BaseModel):
    id: str
    client: Client
    calculator: DPMCalculator

    class Config:
        arbitrary_types_allowed = True

    def empty_action_playlog(self) -> PlayLog:
        return PlayLog(
            events=[],
            view=self.get_simulation_view(),
            clock=self.client.environment.show("clock"),
            action=Action(name="*", method="elapse", payload=0),
        )

    def get_simulation_view(self) -> SimulationView:
        return SimulationView(
            validity_view={v.name: v for v in self.client.environment.show("validity")},
            running_view={v.name: v for v in self.client.environment.show("running")},
            buff_view=self.client.environment.show("buff"),
        )

    def dispatch(self, action: Action) -> PlayLog:
        events = self.client.play(action)

        return PlayLog(
            clock=self.client.environment.show("clock"),
            view=self.get_simulation_view(),
            action=action,
            events=events,
        )


class WorkspaceRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def add(self, workspace: Workspace) -> None:
        ...

    @abc.abstractmethod
    def get(self, workspace_id: str) -> Optional[Workspace]:
        ...

    @abc.abstractmethod
    def update(self, workspace: Workspace) -> None:
        ...
