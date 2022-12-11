import uuid
from typing import Any

import fastapi
import pydantic
from fastapi import Depends

from simaple.core.base import ActionStat, Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.simulate.base import Action, Event
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.kms import get_client
from simaple.simulate.report.base import Report
from simaple.simulate.report.dpm import DPMCalculator, LevelAdvantage
from simaple.simulate.reserved_names import Tag

router = fastapi.APIRouter(prefix="/workspace")

_workspaces: dict = {}
_logs: dict = {}


def get_workspace():
    return _workspaces


def get_logs():
    return _logs


class WorkspaceConfiguration(pydantic.BaseModel):
    action_stat: ActionStat
    groups: list[str]
    injected_values: dict[str, Any]
    skill_levels: dict[str, int]
    v_improvements: dict[str, int]
    character_stat: Stat


class WorkspaceResponse(pydantic.BaseModel):
    id: str


@router.post("", response_model=WorkspaceResponse)
def create(
    conf: WorkspaceConfiguration,
    workspace=Depends(get_workspace),
    logs=Depends(get_logs),
) -> Any:
    workspace_id = str(uuid.uuid4())
    client = get_client(
        conf.action_stat,
        conf.groups,
        conf.injected_values,
        conf.skill_levels,
        conf.v_improvements,
    )

    damage_calculator = DPMCalculator(
        character_spec=conf.character_stat,
        damage_logic=INTBasedDamageLogic(attack_range_constant=1.2, mastery=0.95),
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
        elemental_resistance_disadvantage=0.5,
    )

    workspace[workspace_id] = {
        "client": client,
        "damage_calculator": damage_calculator,
    }

    response = PlayResponse(
        events=[],
        index=0,
        validity_view=client.environment.show("validity"),
        running_view=client.environment.show("running"),
        buff_view=client.environment.show("buff"),
        damage=0,
    )

    logs[workspace_id] = [
        (
            client.environment.store.save(),
            Action(name="*", method="elapse", payload=0),
            response,
        )
    ]
    return WorkspaceResponse(id=workspace_id)


class PlayResponse(pydantic.BaseModel):
    events: list[Event]
    index: int
    validity_view: list[Validity]
    running_view: list[Running]
    buff_view: Stat
    damage: float


@router.post("/play/{workspace_id}", response_model=PlayResponse)
def play(
    workspace_id: str,
    action: Action,
    workspace=Depends(get_workspace),
    logs=Depends(get_logs),
) -> PlayResponse:

    client = workspace[workspace_id]["client"]
    damage_calculator = workspace[workspace_id]["damage_calculator"]

    current_log = logs[workspace_id]
    events = client.play(action)
    event_index = len(current_log) + 1
    buff_view = client.environment.show("buff")

    report = Report()
    for event in events:
        if event.tag == Tag.DAMAGE:
            report.add(0, event, buff_view)

    damage = damage_calculator.calculate_damage(report)

    response = PlayResponse(
        events=events,
        index=event_index,
        validity_view=client.environment.show("validity"),
        running_view=client.environment.show("running"),
        buff_view=client.environment.show("buff"),
        damage=damage,
    )

    current_log.append(
        (client.environment.store.save(), action, response),
    )

    return response


@router.get("/{workspace_id}/logs/{log_id}", response_model=PlayResponse)
def get_log(
    workspace_id: str,
    log_id: int,
    workspace=Depends(get_workspace),
    logs=Depends(get_logs),
) -> PlayResponse:
    current_log = logs[workspace_id]
    _, __, resp = current_log[log_id]

    return resp
