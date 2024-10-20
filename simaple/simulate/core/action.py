from pydantic import ConfigDict
from typing_extensions import TypedDict


class Action(TypedDict):
    """
    Action is primitive value-object which indicated
    what `Component` and Which `method` will be triggerd.
    """

    name: str
    method: str
    payload: int | str | float | dict | None


setattr(Action, "__pydantic_config__", ConfigDict(extra="forbid"))

ActionSignature = tuple[str, str]


def get_action_signature(action: Action) -> ActionSignature:
    return action["name"], action["method"]


EventCallback = tuple[Action, Action]

class ElapseActionPayload(TypedDict):
    """
    ElapseAction is a primitive value-object which indicated
    how much time will be elapsed.
    """

    time: float


class UseActionPayload(TypedDict):
    ...
