from typing import Callable, TypedDict

from simaple.simulate.core import Action, Event
from simaple.simulate.core.store import Store

ReducerType = Callable[[Action, Store], list[Event]]


class ReducerPrecursor(TypedDict): ...
