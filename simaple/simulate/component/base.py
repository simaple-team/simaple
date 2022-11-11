import inspect
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Optional, Type, Union

from pydantic import BaseModel, Field

from simaple.simulate.base import Action, Dispatcher, Environment, Event, State, Store
from simaple.simulate.event import EventProvider, NamedEventProvider
from simaple.simulate.global_property import GlobalProperty
from simaple.spec.loadable import TaggedNamespacedABCMeta

WILD_CARD = "*"


ReducerType = Callable[..., tuple[Union[tuple[State], State], Any]]


class ComponentMethodWrapper:
    def __init__(self, func: ReducerType, skip_count=1):
        self._func = func
        self._has_payload = skip_count == 1
        self._input_state_names = [
            param.name for param in inspect.signature(func).parameters.values()
        ][
            skip_count:
        ]  # skip self, payload
        self._payload_type: Type[BaseModel] = list(
            inspect.signature(func).parameters.values()
        )[0].annotation

    def __call__(self, *args, **kwargs) -> tuple[Union[tuple[State], State], Any]:
        return self._func(*args, **kwargs)

    def translate_payload(self, payload: Optional[Union[int, str, dict]]):
        if not self._has_payload:
            raise ValueError("no skip_count do not support payload translation")

        if not isinstance(payload, dict) or self._payload_type is None:
            return payload

        return self._payload_type.parse_obj(payload)

    def get_states(self, store: Store, default_states, binds=None):
        return [
            store.read_state(name, default=default_states.get(name, None))
            for name in self._get_bound_names(binds)
        ]

    def set_states(self, store: Store, states, binds=None):
        for name, state in zip(self._get_bound_names(binds), states):
            store.set_state(name, state)

    def _get_bound_names(self, binds: Optional[dict[str, str]] = None) -> list[str]:
        if binds is None:
            binds = {}

        return [
            (binds[name] if name in binds else name) for name in self._input_state_names
        ]


def reducer_method(func):
    func.__isreducer__ = True

    return func


def view_method(func):
    func.__isview__ = True

    return func


class ActionRouter(BaseModel, metaclass=ABCMeta):
    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    def is_enabled_action(self, action: Action):
        ...

    @abstractmethod
    def get_matching_reducer(self, action: Action) -> ComponentMethodWrapper:
        ...

    @abstractmethod
    def get_matching_method_name(self, action: Action) -> str:
        ...


class ConcreteActionRouter(ActionRouter):
    mappings: dict[str, ComponentMethodWrapper]
    method_mappings: dict[str, str]

    def is_enabled_action(self, action: Action):
        return action.signature in self.mappings

    def get_matching_reducer(self, action: Action) -> ComponentMethodWrapper:
        return self.mappings[action.signature]

    def get_matching_method_name(self, action: Action) -> str:
        return self.method_mappings[action.signature]


class ReducerMethodWrappingDispatcher(Dispatcher):
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
        if binds is None:
            binds = {}

        binds.update(GlobalProperty.get_default_binds())

        self._binds = binds

    def __call__(self, action: Action, store: Store) -> list[Event]:
        if not self._action_router.is_enabled_action(action):
            return []

        local_store = store.local(self._name)

        reducer = self._action_router.get_matching_reducer(action)
        method_name = self._action_router.get_matching_method_name(action)

        input_states = reducer.get_states(
            local_store, self._default_state, binds=self._binds
        )
        output_states, maybe_events = reducer(
            reducer.translate_payload(action.payload), *input_states
        )

        reducer.set_states(
            local_store,
            self.regularize_returned_state(output_states),
            binds=self._binds,
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


class WrappedView:
    def __init__(
        self,
        name: str,
        wrapped_view_method: ComponentMethodWrapper,
        default_state: dict[str, State],
        binds=None,
    ):
        self._name = name
        self._default_state = default_state
        self._wrapped_view_method = wrapped_view_method
        self._binds = binds

    def __call__(self, store: Store):
        local_store = store.local(self._name)
        input_states = self._wrapped_view_method.get_states(
            local_store, self._default_state
        )
        view = self._wrapped_view_method(*input_states)

        return view


class ComponentMetaclass(TaggedNamespacedABCMeta("Component")):
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        previous_reducers = set()
        for base in bases:
            previous_reducers.update(getattr(base, "__reducers__", {}))

        reducers = {
            name
            for name, value in namespace.items()
            if getattr(value, "__isreducer__", False)
        }
        reducers.update(previous_reducers)
        cls.__reducers__ = frozenset(reducers)

        previous_views = set()
        for base in bases:
            previous_views.update(getattr(base, "__views__", {}))

        views = {
            name
            for name, value in namespace.items()
            if getattr(value, "__isview__", False)
        }
        views.update(previous_views)
        cls.__views__ = frozenset(views)

        return cls


class Component(BaseModel, metaclass=ComponentMetaclass):
    """
    Component is compact bundle of state-action.
    Component provides state and it's handler - a "reducer" which instance method decorated by @reducer_method.

    "Primary Component" is passive-component. This only listen actions and change its state.
    "Active Component" may impact to other components. This side-effects are called as "EventHandler".
    EventHandlers, will require target components, can be generated by install(*args) or manually created.

    Component는 연관된 상태-변화 메서드의 집합입니다.
    모든 reducer는 다음과 같은 형태를 준수해야 합니다.
    (payload, ...states) => (states, optional[list[event]])

    Component는 어떠한 상태도 가지지 않는 순수-함수로서 기능해야만 합니다.
    """

    name: str
    listening_actions: dict[str, str] = Field(default_factory=dict)
    binds: dict[str, str] = Field(default_factory=dict)

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

    def add_to_environment(self, environment: Environment):
        dispatcher = self.export_dispatcher()
        environment.add_dispatcher(dispatcher)

        for view_name, view in self.get_views().items():
            environment.add_view(f"{self.name}.{view_name}", view)

    def get_action_router(self) -> ActionRouter:
        reducer_methods = self.get_reducer_methods()

        wild_card_mappings = {
            f"{WILD_CARD}.{method}": method for method in reducer_methods.keys()
        }
        default_mappings = {
            f"{self.name}.{method}": method for method in reducer_methods.keys()
        }
        method_mappings = {}
        method_mappings.update(default_mappings)
        method_mappings.update(wild_card_mappings)
        method_mappings.update(self.listening_actions)

        reducer_mappings = {k: reducer_methods[v] for k, v in method_mappings.items()}

        return ConcreteActionRouter(
            method_mappings=method_mappings, mappings=reducer_mappings
        )

    def export_dispatcher(self) -> Dispatcher:
        return ReducerMethodWrappingDispatcher(
            self.name,
            self.get_action_router(),
            self.get_default_state(),
            binds=self.binds,
        )

    def get_reducer_methods(self):
        return {
            method_name: ComponentMethodWrapper(getattr(self, method_name))
            for method_name in getattr(self, "__reducers__")
        }

    def get_views(self):
        return {
            method_name: WrappedView(
                self.name,
                ComponentMethodWrapper(getattr(self, method_name), skip_count=0),
                self.get_default_state(),
                binds=self.binds,
            )
            for method_name in getattr(self, "__views__")
        }
