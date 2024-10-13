from __future__ import annotations

from typing import Optional, Union

from pydantic import BaseModel, ConfigDict
from typing_extensions import TypedDict

# from simaple.simulate.core.action import Action
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


class Entity(BaseModel, metaclass=TaggedNamespacedABCMeta(kind="Entity")): ...


class Event(TypedDict):
    """
    Event is primitive value-object, which indicated
    "something happened" via action-handlers.

    Event may verbose; Any applications will watch event stream to
    take some activities. Actions are only for internal state-change;
    only events are externally shown.
    """

    name: str
    payload: dict
    method: str
    tag: Optional[str]
    handler: Optional[str]


setattr(Event, "__pydantic_config__", ConfigDict(extra="forbid"))
