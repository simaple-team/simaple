import pydantic

from simaple.core.base import ActionStat, Stat
from simaple.simulate.base import Action, Event
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.report.base import Report
from simaple.simulate.reserved_names import Tag


class PlayLog(pydantic.BaseModel):
    events: list[Event]
    index: int
    validity_view: dict[str, Validity]
    running_view: dict[str, Running]
    buff_view: Stat
    clock: float
    damage: float
    delay: float
    action: Action


_workspaces: dict = {}
_logs: dict[str, list[dict, PlayLog]] = {}


def get_workspace():
    return _workspaces


def get_logs():
    return _logs


def get_play_logs(workspace_id, logs) -> list[PlayLog]:
    verbose_logs = logs[workspace_id]
    return [pl for _, pl in verbose_logs]


def add_play_log(workspace, logs, log: PlayLog) -> None:
    logs.append(
        (workspace["client"].environment.store.save(), log),
    )


def dispatch_action(workspace, logs, action: Action) -> PlayLog:
    client = workspace["client"]
    damage_calculator = workspace["damage_calculator"]

    current_log = logs
    events = client.play(action)
    event_index = len(current_log) + 1
    buff_view = client.environment.show("buff")

    report = Report()
    for event in events:
        if event.tag == Tag.DAMAGE:
            report.add(0, event, buff_view)

    delay = 0
    for event in events:
        if event.tag in (Tag.DELAY,) and event.payload["time"] > 0:
            delay += event.payload["time"]

    damage = damage_calculator.calculate_damage(report)

    response = PlayLog(
        events=events,
        index=event_index,
        validity_view={v.name: v for v in client.environment.show("validity")},
        running_view={v.name: v for v in client.environment.show("running")},
        buff_view=client.environment.show("buff"),
        clock=client.environment.show("clock"),
        damage=damage,
        delay=delay,
        action=action,
    )

    return response
