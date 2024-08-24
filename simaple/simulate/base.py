from __future__ import annotations

import re
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Any, Callable, Optional, TypeVar, Union, cast

from pydantic import BaseModel
from typing_extensions import TypedDict

from simaple.simulate.reserved_names import Tag
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
    get_class,
)


class Entity(BaseModel, metaclass=TaggedNamespacedABCMeta(kind="Entity")): ...


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
    def read_entity(self, name: str, default: Optional[Entity]): ...

    @abstractmethod
    def set_entity(self, name: str, entity: Entity): ...

    @abstractmethod
    def local(self, address: str) -> Store: ...

    @abstractmethod
    def save(self) -> Any: ...

    @abstractmethod
    def load(self, saved_store) -> None: ...


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
    def __call__(self, action: Action, store: Store) -> list[Event]: ...

    @abstractmethod
    def includes(self, signature: str) -> bool: ...

    @abstractmethod
    def init_store(self, store: Store) -> None: ...


def named_dispatcher(direction: str):
    def decorator(dispatcher: Dispatcher):
        def _includes(signature: str) -> bool:
            return signature == direction

        def _init_store(store: Store) -> None:
            return

        setattr(dispatcher, "includes", _includes)
        setattr(dispatcher, "init_store", _init_store)
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

    def init_store(self, store: Store) -> None:
        for dispatcher in self._dispatchers:
            dispatcher.init_store(store)


View = Callable[[Store], Any]


EventCallback = tuple[Action, Action]


def _get_event_callbacks(event: Event) -> EventCallback:
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


class Checkpoint(BaseModel):
    store_ckpt: dict[str, Any]

    @classmethod
    def create(
        cls,
        store: AddressedStore,
    ) -> Checkpoint:
        return Checkpoint(store_ckpt=store.save())

    def restore(self) -> AddressedStore:
        concrete_store = ConcreteStore()
        concrete_store.load(self.store_ckpt)
        store = AddressedStore(concrete_store)
        return store


ViewerType = Callable[[str], Any]


class ViewSet:
    def __init__(self) -> None:
        self._views: dict[str, View] = {}

    def add_view(self, view_name: str, view: View) -> None:
        self._views[view_name] = view

    def show(self, view_name: str, store: Store) -> Any:
        return self._views[view_name](store)

    def get_views(self, view_name_pattern: str) -> list[View]:
        regex = re.compile(view_name_pattern)
        return [
            view for view_name, view in self._views.items() if regex.match(view_name)
        ]

    def get_viewer_from_ckpt(self, ckpt: Checkpoint) -> ViewerType:
        return self.get_viewer(ckpt.restore())

    def get_viewer(self, store: Store) -> ViewerType:
        def _viewer(view_name: str) -> Any:
            return self.show(view_name, store)

        return _viewer


class PostActionCallback:
    """
    PostActionCallback receives "Event" and do any post-action operations.
    PostActionCallback receives viewer; this ensure callback can read every state, but cannot modify.
    """

    def __call__(
        self, event: Event, viewer: ViewerType, all_events: list[Event]
    ) -> None: ...


class PreviousCallback(Entity):
    events: list[EventCallback]


S = TypeVar("S", bound=Store)


def play(store: S, action: Action, router: RouterDispatcher) -> tuple[S, list[Event]]:
    events: list[Event] = []
    action_queue = [action]

    previous_callbacks = store.read_entity(
        "previous_callbacks", default=PreviousCallback(events=[])
    )

    # Join proposed action with previous event's callback
    for emitted_callback, done_callback in previous_callbacks.events:
        action_queue = [emitted_callback] + action_queue + [done_callback]

    for target_action in action_queue:
        resolved_events = router(target_action, store)
        events += resolved_events

    # Save untriggered callbacks
    store.set_entity(
        "previous_callbacks",
        PreviousCallback(events=[_get_event_callbacks(event) for event in events]),
    )

    return store, events


class PlayLog(BaseModel):
    clock: float

    action: Action
    events: list[Event]
    checkpoint: Checkpoint

    def get_delay_left(self) -> float:
        delay = 0
        for event in self.events:
            if event["tag"] in (Tag.DELAY,):
                if event["payload"]["time"] > 0:
                    delay += event["payload"]["time"]

        return delay
