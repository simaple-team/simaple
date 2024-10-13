from typing import TypedDict, TypeVar

from simaple.simulate.component.entity import Cooldown, Lasting, Stack
from simaple.simulate.component.view import KeydownView, Running, Validity
from simaple.simulate.core import Event
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class _State(TypedDict):
    cooldown: Cooldown
    lasting: Lasting
    stack: Stack
    dynamics: Dynamics


_StateT = TypeVar("_StateT", bound=_State)
