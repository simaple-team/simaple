import copy
import re
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Optional, Union

from pydantic import BaseModel, Extra


class State(BaseModel):
    ...


class Action(BaseModel):
    """
    Action is primitive value-object which indicated
    what `Component` and Which `method` will be triggerd.
    """

    name: str
    method: str
    payload: Optional[Union[int, str, dict]]

    class Config:
        extra = Extra.forbid

    @property
    def signature(self) -> str:
        if len(self.method) == 0:
            return self.name

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
    method: str = ""
    tag: Optional[str]
    handler: Optional[str]
    payload: Any

    class Config:
        extra = Extra.forbid

    @property
    def signature(self) -> str:
        if len(self.method) == 0:
            return self.name

        return f"{self.name}.{self.method}"


class Store(metaclass=ABCMeta):
    def use_state(self, name: str, default: State):
        def state_setter(state):
            self.set_state(name, state)

        return self.read_state(name, default=default), state_setter

    @abstractmethod
    def read_state(self, name: str, default: State):
        ...

    @abstractmethod
    def set_state(self, name: str, state: State):
        ...

    @abstractmethod
    def local(self, address: str):
        ...


class ConcreteStore(Store):
    def __init__(self):
        self._states: dict[str, State] = {}

    def set_state(self, name: str, state: State):
        self._states[name] = state

    def read_state(self, name: str, default: State):
        value = self._states.setdefault(name, default)
        if value is None:
            raise ValueError(
                "None-default only enabled for external-property binding. Maybe missing global proeperty installation?"
            )
        return value.copy()

    def local(self, address):
        return self


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


DispatcherType = Callable[[Action, Store], list[Event]]


class Dispatcher(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, action: Action, store: Store):
        ...


View = Callable[[Store], Any]


class Environment:
    def __init__(self, store: AddressedStore):
        self.dispatchers: list[DispatcherType] = []
        self.store = store
        self._views = {}

    def add_dispatcher(self, dispatcher: DispatcherType):
        self.dispatchers.append(dispatcher)

    def add_view(self, view_name: str, view: View):
        self._views[view_name] = view

    def resolve(self, action: Action) -> list[Event]:
        events = []
        for dispatcher in self.dispatchers:
            events += dispatcher(action, self.store)

        return events

    def show(self, view_name: str):
        return self._views[view_name](self.store)

    def get_views(self, view_name_pattern: str) -> list[View]:
        regex = re.compile(view_name_pattern)
        return [
            view for view_name, view in self._views.items() if regex.match(view_name)
        ]


class EventHandler:
    """
    EventHandler receives "Event" and create "Action" (maybe multiple).
    Eventhandler receives full context; to provide meaningful decision.
    Handling given store is not recommended "strongly". Please use store with
    read-only mode as possible as you can.
    """

    def __call__(
        self, event: Event, environment: Environment, all_events: list[Event]
    ) -> Optional[list[Action]]:
        ...


class Client:
    def __init__(self, environment: Environment):
        self.environment = environment
        self._event_handlers = []

    def add_handler(self, event_handler: EventHandler):
        self._event_handlers.append(event_handler)

    def handle(
        self, event: Event, environment: Environment, all_events: list[Event]
    ) -> list[Action]:
        actions = []
        for handler in self._event_handlers:
            requested_actions = handler(event, environment, all_events)
            if requested_actions is not None:
                actions += requested_actions

        return actions

    def play(self, base_action: Action) -> list[Event]:
        actions = [base_action]
        events: list[Event] = []
        all_events: list[Event] = []

        while len(actions) > 0:
            events = []
            for action in actions:
                resolved_events = self.environment.resolve(action)
                all_events += resolved_events
                events += resolved_events
            actions = []
            for event in events:
                actions += self._wrap_relay_decision(
                    event, self.handle(event, self.environment, events)
                )

        return all_events

    def _wrap_relay_decision(self, event, relay_decision: list[Action]) -> list[Action]:
        """Wrap-up relay's decision by built-in actionss
        These decisions must provided; this is "forced action"
        """
        emiited_event_action = Action(
            name=event.name,
            method=f"{event.method}.emitted.{event.tag or ''}",
            payload=copy.deepcopy(event.payload),
        )

        done_event_action = Action(
            name=event.name,
            method=f"{event.method}.done.{event.tag or ''}",
            payload=copy.deepcopy(event.payload),
        )

        return [emiited_event_action] + relay_decision + [done_event_action]
