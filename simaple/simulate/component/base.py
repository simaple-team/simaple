import inspect
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Optional, Type, Union

from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError

from simaple.simulate.base import Action, Dispatcher, Entity, Environment, Event, Store
from simaple.simulate.event import EventProvider, NamedEventProvider
from simaple.simulate.global_property import GlobalProperty
from simaple.spec.loadable import TaggedNamespacedABCMeta

WILD_CARD = "*"


ReducerType = Callable[..., tuple[Union[tuple[Entity], Entity], Any]]


class ReducerState(BaseModel):
    ...


class ComponentMethodWrapper:
    def __init__(self, func: ReducerType, skip_count=1):
        self._func = func
        self._has_payload = skip_count == 1

        self._payload_type: Optional[Type[BaseModel]] = None
        if len(inspect.signature(func).parameters.values()) > 0:
            self._payload_type = list(inspect.signature(func).parameters.values())[
                0
            ].annotation

        self._state_type = list(inspect.signature(func).parameters.values())[
            skip_count
        ].annotation

    def __call__(self, *args, **kwargs) -> tuple[Union[tuple[Entity], Entity], Any]:
        return self._func(*args, **kwargs)

    def translate_payload(self, payload: Optional[Union[int, str, dict]]):
        if not self._has_payload:
            raise ValueError("no skip_count do not support payload translation")

        if not isinstance(payload, dict) or self._payload_type is None:
            return payload

        return self._payload_type.parse_obj(payload)

    def get_state_type(self):
        return self._state_type


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


class StoreAdapter:
    def __init__(
        self,
        default_state: dict[str, Entity],
        binds=None,
    ):
        self._default_state = default_state
        if binds is None:
            binds = {}
        binds.update(GlobalProperty.get_default_binds())

        self._binds = binds

    def get_state(self, store: Store, state_type):
        entities = {
            name: store.read_state(address, default=self._default_state.get(name))
            for name, address in self._get_bound_names().items()
        }

        return state_type(**entities)

    def set_state(self, store: Store, state):
        bounded_names = self._get_bound_names()

        for name, entity in dict(state).items():
            if name in bounded_names:
                store.set_state(bounded_names[name], entity)

    def _get_bound_names(self) -> dict[str, str]:
        names = {name: name for name in self._default_state}
        names.update(self._binds)

        return names


class ReducerMethodWrappingDispatcher(Dispatcher):
    def __init__(
        self,
        name: str,
        action_router: ActionRouter,
        default_state: dict[str, Entity],
        binds=None,
    ):
        self._name = name
        self._default_state = default_state
        self._action_router = action_router
        self._store_adapter = StoreAdapter(self._default_state, binds)

    def init_states(self, store: Store):
        local_store = store.local(self._name)
        for name in self._default_state:
            local_store.read_state(name, default=self._default_state[name])

    def __call__(self, action: Action, store: Store) -> list[Event]:
        if not self._action_router.is_enabled_action(action):
            return []

        local_store = store.local(self._name)

        reducer = self._action_router.get_matching_reducer(action)
        method_name = self._action_router.get_matching_method_name(action)

        input_state = self._store_adapter.get_state(
            local_store, reducer.get_state_type()
        )
        output_state, maybe_events = reducer(
            reducer.translate_payload(action.payload), input_state
        )

        self._store_adapter.set_state(
            local_store,
            output_state,
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
        default_state: dict[str, Entity],
        binds=None,
    ):
        self._name = name
        self._default_state = default_state
        self._wrapped_view_method = wrapped_view_method
        self._store_adapter = StoreAdapter(self._default_state, binds)

    def __call__(self, store: Store):
        local_store = store.local(self._name)
        try:
            input_state = self._store_adapter.get_state(
                local_store, self._wrapped_view_method.get_state_type()
            )
            view = self._wrapped_view_method(input_state)

            return view
        except ValidationError as e:
            raise ValueError(f"Error raised from {self._name}\n{e}") from e


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


class StoreEmbeddedObject:
    def __init__(self, name, store: Store, default_states: dict):
        self.name = name
        self._store = store
        self._default_states = default_states

    def __getattr__(self, k):
        if k in self._default_states:
            return self._store.local(self.name).read_state(
                k, default=self._default_states.get(k, None)
            )

        raise AttributeError(f"No attribute: {k}")

    def __setattr__(self, k, v):
        if k in ["name", "_store", "_default_states"]:
            super().__setattr__(k, v)
        elif k in self._default_states:
            self._store.local(self.name).set_state(k, v)
        else:
            super().__setattr__(k, v)


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
    def get_default_state(self) -> dict[str, Entity]:
        ...

    @property
    def event_provider(self) -> EventProvider:
        return NamedEventProvider(self.name)

    def add_to_environment(self, environment: Environment):
        dispatcher = self.export_dispatcher()
        environment.add_dispatcher(dispatcher)
        dispatcher.init_states(environment.store)

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

    def export_dispatcher(self) -> ReducerMethodWrappingDispatcher:
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

    def compile(self, initialized_store: Store) -> StoreEmbeddedObject:
        """
        Return store-embedded object which supports contracted interface of current component.
        """

        def get_compiled_reducer(method_name, dispatcher, store):
            def compiled_reducer(payload):
                action = Action(name=self.name, method=method_name, payload=payload)
                return dispatcher(action, store)

            return compiled_reducer

        def get_compiled_view(view, store):
            def compiled_view():
                return view(store)

            return compiled_view

        compiled_component = StoreEmbeddedObject(
            self.name, initialized_store, self.get_default_state()
        )
        exported_dispatcher = self.export_dispatcher()

        for reducer_name in self.get_reducer_methods():
            setattr(
                compiled_component,
                reducer_name,
                get_compiled_reducer(
                    reducer_name, exported_dispatcher, initialized_store
                ),
            )

        for view_name, view in self.get_views().items():
            setattr(
                compiled_component,
                view_name,
                get_compiled_view(view, initialized_store),
            )

        return compiled_component
