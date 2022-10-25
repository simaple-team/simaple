from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Optional

from pydantic import BaseModel


class State(BaseModel):
    ...


class Action(BaseModel):
    """
    Action is primitive value-object which indicated
    what `Component` and Which `method` will be triggerd.
    """

    name: str
    method: str
    payload: Any

    @property
    def signature(self) -> str:
        return f"{self.name}.{self.method}"


class Event(BaseModel):
    """
    Event is primitive value-object, which indicated
    "something happened" via action-handlers.

    Event may verbose; Any applications will watch event stream to
    take some activities. Actions are only for internal state-change;
    only events are externally shown.
    """

    name: str
    method: Optional[str]
    tag: Optional[str]
    handler: Optional[str]

    @property
    def signature(self) -> str:
        return f"{self.name}.{self.handler}"


class EventHandler:
    """
    EventHandler receives "Event" and create "Action" (maybe multiple).
    """

    def dispatch(self, event: Event) -> Optional[list[Action]]:
        ...


class SignatureEventHandler(EventHandler):
    def __init__(self, allowed_signatures: list, action: Action):
        self.allowed_signatures = allowed_signatures
        self._action = action

    def dispatch(self, event: Event) -> Optional[list[Action]]:
        if event.signature in self.allowed_signatures:
            return [self._action.copy()]

        return None


class Store(metaclass=ABCMeta):
    def use_state(self, name: str, default: State):
        return self.read_state(name, default=default), self.set_state

    @abstractmethod
    def read_state(self, name: str, default: State):
        """This returns read-only state; changes will not affect stored state"""

    @abstractmethod
    def set_state(self, name: str, state: State):
        ...


class ConcreteStore(Store):
    def __init__(self):
        self._states: dict[str, State] = {}

    def set_state(self, name: str, state: State):
        self._states[name] = state

    def read_state(self, name: str, default: State):
        value = self._states.setdefault(name, default)
        return value.copy()


class AddressedStore(Store):
    def __init__(self, concrete_store: ConcreteStore, current_address: str = ""):
        self._current_address = current_address
        self._concrete_store = concrete_store

    def set_state(self, name: str, state: State):
        address = self._resolve_address(name)
        return self._concrete_store.set_state(address, state)

    def read_state(self, name: str, default: State):
        address = self._resolve_address(name)
        return self._concrete_store.read_state(address, default)

    def local(self, address: str):
        return AddressedStore(
            self._concrete_store, f"{self._current_address}.{address}"
        )

    def _resolve_address(self, name: str):
        """descriminate local-variable (no period) and global-variable (with period)"""
        if len(name.split(".")) == 1:
            return f"{self._current_address}.{name}"

        return name


class Actor:
    def __init__(self):
        super().__init__()
        self._event_handlers = []

    def add_dispatcher(self, event_handler: EventHandler):
        self._event_handlers.append(event_handler)

    def handle(self, event: Event) -> list[Action]:
        ...


DispatcherType = Callable[[Action, Store], tuple[Event]]


class Dispatcher(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, action: Action, store: Store):
        ...


class Reducer:
    def __init__(self, store: AddressedStore):
        self.dispatchers: dict[str, DispatcherType] = {}
        self.store = store

    def add_reducer(self, signature: str, dispatcher: DispatcherType):
        self.dispatchers[signature] = dispatcher

    def resolve(self, action: Action) -> tuple[Event]:
        local_store = self.store.local(action.name)
        return self.dispatchers[action.signature](action, local_store)


class View(metaclass=ABCMeta):
    @abstractmethod
    def aggregate(self, components):
        ...
