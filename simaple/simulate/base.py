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

    @abstractmethod
    def save(self) -> Any:
        ...

    @abstractmethod
    def load(self, saved_store) -> None:
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

    def save(self) -> Any:
        return {k: v.copy() for k, v in self._states.items()}

    def load(self, saved_store: dict[str, State]) -> None:
        self._states = {k: v.copy() for k, v in saved_store.items()}


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

    def save(self):
        return self._concrete_store.save()

    def load(self, saved_store):
        return self._concrete_store.load(saved_store)


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
        self._views: dict[str, View] = {}

    def add_dispatcher(self, dispatcher: DispatcherType):
        self.dispatchers.append(dispatcher)

    def add_view(self, view_name: str, view: View):
        self._views[view_name] = view

    def resolve(self, action: Action) -> list[Event]:
        events = []
        for dispatcher in self.dispatchers:
            try:
                events += dispatcher(action, self.store)
            except Exception as e:
                raise Exception(
                    f"Exception raised during resolving {action.signature}"
                ) from e
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
    ) -> None:
        ...


EventCallback = tuple[Action, Action]


class Client:
    def __init__(self, environment: Environment):
        self.environment = environment
        self._event_handlers: list[EventHandler] = []
        self._previous_callbacks: list[EventCallback] = []

    def add_handler(self, event_handler: EventHandler) -> None:
        self._event_handlers.append(event_handler)

    def play(self, action: Action) -> list[Event]:
        events: list[Event] = []
        action_queue = [action]

        # Join proposed action with previous event's callback
        for emitted_callback, done_callback in self._previous_callbacks:
            action_queue = [emitted_callback] + action_queue + [done_callback]

        for target_action in action_queue:
            resolved_events = self.environment.resolve(target_action)
            events += resolved_events

        for event in events:
            self._handle(event, self.environment, events)

        # Save untriggered callbacks
        self._previous_callbacks = [
            self._get_event_callbacks(event) for event in events
        ]

        return events

    def clean(self) -> None:
        self._previous_callbacks = []

    def _handle(
        self, event: Event, environment: Environment, all_events: list[Event]
    ) -> None:
        for handler in self._event_handlers:
            handler(event, environment, all_events)

    def _get_event_callbacks(self, event: Event) -> EventCallback:
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

        return (emiited_event_action, done_event_action)
