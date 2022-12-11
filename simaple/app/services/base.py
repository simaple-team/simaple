import pydantic

from simaple.core.base import ActionStat, Stat
from simaple.simulate.base import Action, Event
from simaple.simulate.component.view import Running, Validity


class PlayLog(pydantic.BaseModel):
    events: list[Event]
    index: int
    validity_view: dict[str, Validity]
    running_view: dict[str, Running]
    buff_view: Stat
    clock: float
    damage: float


_workspaces: dict = {}
_logs: dict[str, list[dict, Action, PlayLog]] = {}


def get_workspace():
    return _workspaces


def get_logs():
    return _logs


def get_play_logs(workspace_id, logs) -> list[PlayLog]:
    verbose_logs = logs[workspace_id]
    return [pl for _, __, pl in verbose_logs]
