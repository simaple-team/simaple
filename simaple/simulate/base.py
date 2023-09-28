from __future__ import annotations

import re
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Optional, Union, cast

from pydantic import BaseModel
from typing_extensions import TypedDict

from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
    get_class,
)


class Entity(BaseModel, metaclass=TaggedNamespacedABCMeta(kind="Entity")):
    ...


class Action(TypedDict):
    """
    Action is primitive value-object which indicated
    what `Component` and Which `method` will be triggerd.
    """

    name: str
    method: str
    payload: Union[int, str, float, dict, None]


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


def message_signature(message: Union[Action, Event]) -> str:
    if len(message["method"]) == 0:
        return message["name"]

    return f"{message['name']}.{message['method']}"


class Store(metaclass=ABCMeta):
    def use_entity(self, name: str, default: Entity):
        def entity_setter(state):
            self.set_entity(name, state)

        return self.read_entity(name, default=default), entity_setter

    @abstractmethod
    def read_entity(self, name: str, default: Optional[Entity]):
        ...

    @abstractmethod
    def set_entity(self, name: str, entity: Entity):
        ...

    @abstractmethod
    def local(self, address: str) -> Store:
        ...

    @abstractmethod
    def save(self) -> Any:
        ...

    @abstractmethod
    def load(self, saved_store) -> None:
        ...


class ConcreteStore(Store):
    def __init__(self) -> None:
        self._entities: dict[str, Entity] = {}

    def set_entity(self, name: str, entity: Entity) -> None:
        self._entities[name] = entity

    def read_entity(self, name: str, default: Optional[Entity]):
        if default is None:
            value = self._entities.get(name)
        else:
            value = self._entities.setdefault(name, default)
        if value is None:
            raise ValueError(
                f"No entity exists: {name}. None-default only enabled for external-property binding. Maybe missing global proeperty installation?"
            )
        return value

    def local(self, address):
        return self

    def save(self) -> Any:
        return {k: self._save_entity(v) for k, v in self._entities.items()}

    def load(self, saved_store: dict[str, dict]) -> None:
        self._entities = {k: self._load_entity(v) for k, v in saved_store.items()}

    def _save_entity(self, entity: Entity) -> dict:
        entity_clsname = entity.__class__.__name__
        return {
            "cls": entity_clsname,
            "payload": entity.model_dump(),
        }

    def _load_entity(self, saved_entity_dict: dict) -> Entity:
        clsname, payload = saved_entity_dict["cls"], saved_entity_dict["payload"]
        return cast(Entity, get_class(clsname, kind="Entity").model_validate(payload))


class AddressedStore(Store):
    def __init__(self, concrete_store: ConcreteStore, current_address: str = ""):
        self._current_address = current_address
        self._concrete_store = concrete_store

    def set_entity(self, name: str, entity: Entity):
        address = self._resolve_address(name)
        return self._concrete_store.set_entity(address, entity)

    def read_entity(self, name: str, default: Optional[Entity]):
        address = self._resolve_address(name)
        return self._concrete_store.read_entity(address, default)

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


class Dispatcher(metaclass=ABCMeta):
    @abstractmethod
    def __call__(self, action: Action, store: Store) -> list[Event]:
        ...

    @abstractmethod
    def includes(self, signature: str) -> bool:
        ...


def named_dispatcher(direction: str):
    def decorator(dispatcher: Dispatcher):
        def _includes(signature: str) -> bool:
            return signature == direction

        setattr(dispatcher, "includes", _includes)
        return dispatcher

    return decorator


class RouterDispatcher(Dispatcher):
    def __init__(self) -> None:
        self._dispatchers: list[Dispatcher] = []
        self._route_cache: dict[str, list[Dispatcher]] = defaultdict(list)

    def install(self, dispatcher: Dispatcher):
        self._dispatchers.append(dispatcher)

    def includes(self, signature: str) -> bool:
        return signature in self._route_cache.keys()

    def __call__(self, action: Action, store: Store) -> list[Event]:
        events = []
        signature = message_signature(action)
        if signature in self._route_cache:
            for dispatcher in self._route_cache[signature]:
                events += dispatcher(action, store)

            return events

        cache = []

        for dispatcher in self._dispatchers:
            if dispatcher.includes(signature):
                cache.append(dispatcher)
                events += dispatcher(action, store)

        self._route_cache[signature] = cache
        return events


View = Callable[[Store], Any]


class Environment:
    def __init__(self, store: AddressedStore):
        self._router = RouterDispatcher()
        self.store = store
        self._views: dict[str, View] = {}

    def add_dispatcher(self, dispatcher: Dispatcher):
        self._router.install(dispatcher)

    def add_view(self, view_name: str, view: View):
        self._views[view_name] = view

    def resolve(self, action: Action) -> list[Event]:
        return self._router(action, self.store)

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

    def export_previous_callbacks(self) -> list[EventCallback]:
        return list(self._previous_callbacks)

    def restore_previous_callbacks(self, callbacks: list[EventCallback]) -> None:
        self._previous_callbacks = callbacks

    def _handle(
        self, event: Event, environment: Environment, all_events: list[Event]
    ) -> None:
        for handler in self._event_handlers:
            handler(event, environment, all_events)

    def _get_event_callbacks(self, event: Event) -> EventCallback:
        """Wrap-up relay's decision by built-in actionss
        These decisions must provided; this is "forced action"
        """
        emiited_event_action: Action = {
            "name": event["name"],
            "method": f"{event['method']}.emitted.{event['tag'] or ''}",
            "payload": event["payload"],
        }

        done_event_action: Action = {
            "name": event["name"],
            "method": f"{event['method']}.done.{event['tag'] or ''}",
            "payload": event["payload"],
        }

        return (emiited_event_action, done_event_action)
