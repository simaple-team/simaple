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
