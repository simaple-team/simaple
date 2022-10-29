import inspect
from abc import ABCMeta, abstractmethod
from typing import Optional, Union

from pydantic import BaseModel, Field

from simaple.simulate.base import (
    Action,
    Dispatcher,
    DispatcherType,
    Event,
    Reducer,
    State,
    Store,
)
from simaple.simulate.event import EventProvider, NamedEventProvider
from simaple.spec.loadable import TaggedNamespacedABCMeta

WILD_CARD = "*"


def dispatcher_method(func):
    input_state_names = [
        param.name for param in inspect.signature(func).parameters.values()
    ][
        2:
    ]  # skip self, payload

    def get_states(store: Store, default_states):
        return [
            store.read_state(name, default=default_states[name])
            for name in input_state_names
        ]

    def set_states(store: Store, states):
        for name, state in zip(input_state_names, states):
            store.set_state(name, state)

    func.__isdispatcher__ = True
    func.input_state_names = input_state_names
    func.get_states = get_states
    func.set_states = set_states

    return func


class ActionRouter(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def is_enabled_action(self, action: Action):
        ...

    @abstractmethod
    def get_matching_dispatcher(self, action: Action) -> DispatcherType:
        ...

    @abstractmethod
    def get_matching_method_name(self, action: Action) -> str:
        ...


class ConcreteActionRouter(ActionRouter):
    mappings: dict[str, DispatcherType]
    method_mappings: dict[str, str]

    def is_enabled_action(self, action: Action):
        return action.signature in self.mappings

    def get_matching_dispatcher(self, action: Action) -> DispatcherType:
        return self.mappings[action.signature]

    def get_matching_method_name(self, action: Action) -> str:
        return self.method_mappings[action.signature]


class DispatcherMethodWrappingDispatcher(Dispatcher):
    def __init__(
        self,
        name: str,
        action_router: ActionRouter,
        default_state: dict[str, State],
        binds=None,
    ):
        self._name = name
        self._default_state = default_state
        self._action_router = action_router
        self._binds = binds

    def __call__(self, action: Action, store: Store) -> list[Event]:
        if not self._action_router.is_enabled_action(action):
            return []

        local_store = store.local(self._name)

        dispatcher = self._action_router.get_matching_dispatcher(action)
        method_name = self._action_router.get_matching_method_name(action)

        input_states = dispatcher.get_states(local_store, self._default_state)
        output_states, maybe_events = dispatcher(action.payload, *input_states)

        dispatcher.set_states(
            local_store, self.regularize_returned_state(output_states)
        )

        events = self.regularize_returned_event(maybe_events)

        return self.tag_events_by_method_name(method_name, events)

    def regularize_returned_event(
        self, maybe_events: Optional[Union[Event, list[Event]]]
    ) -> list[Event]:
        if maybe_events is None:
            return []

        if isinstance(maybe_events, Event):
            return [maybe_events]

        return maybe_events

    def regularize_returned_state(
        self, maybe_state_tuple: Union[tuple[State], State]
    ) -> tuple[State]:
        if not isinstance(maybe_state_tuple, tuple):
            return (maybe_state_tuple,)

        return maybe_state_tuple

    def tag_events_by_method_name(
        self, method_name: str, events: list[Event]
    ) -> list[Event]:
        tagged_events = []
        for event in events:
            tagged_event = event.copy()
            tagged_event.method = method_name
            if tagged_event.tag is None:
                tagged_event.tag = method_name

            tagged_events.append(tagged_event)

        return tagged_events


def component_view(func):
    func.__component_view__ = True
    return func


class ComponentMetaclass(TaggedNamespacedABCMeta("Component")):
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        previous_dispatchers = set()
        for base in bases:
            previous_dispatchers.update(getattr(base, "__dispatchers__", {}))

        dispatchers = {
            name
            for name, value in namespace.items()
            if getattr(value, "__isdispatcher__", False)
        }
        dispatchers.update(previous_dispatchers)
        cls.__dispatchers__ = frozenset(dispatchers)
        return cls


class Component(BaseModel, metaclass=ComponentMetaclass):
    """
    Component is compact bundle of state-action.
    Component provides state and it's handler - a "dispatcher" which instance method decorated by @dispatcher_method.

    "Primary Component" is passive-component. This only listen actions and change its state.
    "Active Component" may impact to other components. This side-effects are called as "EventHandler".
    EventHandlers, will require target components, can be generated by install(*args) or manually created.

    Component는 연관된 상태-변화 메서드의 집합입니다.
    모든 dispatcher는 다음과 같은 형태를 준수해야 합니다.
    (payload, ...states) => (states, optional[list[event]])

    Component는 어떠한 상태도 가지지 않는 순수-함수로서 기능해야만 합니다.
    """

    name: str
    listening_actions: dict[str, DispatcherType] = Field(default_factory=dict)

    class Config:
        # extra = Extra.forbid
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    @abstractmethod
    def get_default_state(self) -> dict[str, State]:
        ...

    @property
    def event_provider(self) -> EventProvider:
        return NamedEventProvider(self.name)

    def add_to_reducer(self, reducer: Reducer, binds=None):
        dispatcher = self.export_dispatcher(binds=binds)
        reducer.add_reducer(dispatcher)

    def get_action_router(self) -> ActionRouter:
        dispatcher_methods = self.get_dispatcher_methods()

        wild_card_mappings = {
            f"{WILD_CARD}.{method}": method for method in dispatcher_methods.keys()
        }
        default_mappings = {
            f"{self.name}.{method}": method for method in dispatcher_methods.keys()
        }
        method_mappings = {}
        method_mappings.update(default_mappings)
        method_mappings.update(wild_card_mappings)
        method_mappings.update(self.listening_actions)

        dispatcher_mappings = {
            k: dispatcher_methods[v] for k, v in method_mappings.items()
        }

        return ConcreteActionRouter(
            method_mappings=method_mappings, mappings=dispatcher_mappings
        )

    def export_dispatcher(self, binds=None) -> Dispatcher:
        return DispatcherMethodWrappingDispatcher(
            self.name,
            self.get_action_router(),
            self.get_default_state(),
            binds=binds,
        )

    def get_dispatcher_methods(self):
        return {
            method_name: getattr(self, method_name)
            for method_name in getattr(self, "__dispatchers__")
        }
