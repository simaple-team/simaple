from __future__ import annotations

import pydantic

from simaple.app.application.exception import UnknownWorkspaceException
from simaple.app.domain.history import PlayLog
from simaple.app.domain.services.statistics import get_cumulative_logs, get_damage_logs
from simaple.app.domain.uow import UnitOfWork
from simaple.app.domain.workspace import Workspace
from simaple.core.base import Stat
from simaple.simulate.base import Action, Event
from simaple.simulate.component.view import Running, Validity


class PlayLogResponse(pydantic.BaseModel):
    events: list[Event]
    index: int
    validity_view: dict[str, Validity]
    running_view: dict[str, Running]
    buff_view: Stat
    clock: float
    damage: float
    delay: float
    action: Action

    @classmethod
    def from_playlog(
        cls, index: int, playlog: PlayLog, workspace: Workspace
    ) -> PlayLogResponse:
        return PlayLogResponse(
            events=playlog.events,
            index=index,
            validity_view=playlog.view.validity_view,
            running_view=playlog.view.running_view,
            buff_view=playlog.view.get_buff(),
            clock=playlog.clock,
            damage=playlog.get_total_damage(workspace.calculator),
            delay=playlog.get_delay(),
            action=playlog.action,
        )


def query_latest_playlog(workspace_id: str, uow: UnitOfWork) -> PlayLogResponse:
    workspace = uow.workspace_repository().get(workspace_id)
    history = uow.history_repository().get(workspace_id)

    if history is None or workspace is None:
        raise UnknownWorkspaceException()

    latest_index = len(history) - 1

    return PlayLogResponse.from_playlog(
        latest_index, history.get(latest_index), workspace
    )


def query_playlog(
    workspace_id: str, log_index: int, uow: UnitOfWork
) -> PlayLogResponse:
    workspace = uow.workspace_repository().get(workspace_id)
    history = uow.history_repository().get(workspace_id)

    if history is None or workspace is None:
        raise UnknownWorkspaceException()

    return PlayLogResponse.from_playlog(log_index, history.get(log_index), workspace)


class StatisticsResponse(pydantic.BaseModel):
    cumulative_x: list[float]
    cumulative_y: list[float]
    value_x: list[float]
    value_y: list[float]


def query_statistics(workspace_id: str, uow: UnitOfWork) -> StatisticsResponse:
    workspace = uow.workspace_repository().get(workspace_id)
    history = uow.history_repository().get(workspace_id)

    if history is None or workspace is None:
        raise UnknownWorkspaceException()

    cumulative_x, cumulative_y = get_cumulative_logs(history, workspace)
    value_x, value_y = get_damage_logs(history, workspace)

    return StatisticsResponse(
        cumulative_x=cumulative_x,
        cumulative_y=cumulative_y,
        value_x=value_x,
        value_y=value_y,
    )
