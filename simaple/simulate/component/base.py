import copy
import inspect
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, NoReturn, Optional, Type, TypeVar, Union, cast

from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError

from simaple.simulate.base import Action, Dispatcher, Entity, Environment, Event, Store
from simaple.simulate.event import EventProvider, NamedEventProvider
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.reserved_names import Tag
from simaple.spec.loadable import TaggedNamespacedABCMeta

WILD_CARD = "*"


ReducerType = Callable[..., tuple[Union[tuple[Entity], Entity], Any]]


T = TypeVar("T", bound=BaseModel)


class ReducerState(BaseModel):
    def copy(self) -> NoReturn:  # type: ignore
        raise NotImplementedError("copy() is disabled in ReducerState")

    def deepcopy(self: T) -> T:
        return super().copy(deep=True)  # type: ignore


class ComponentMethodWrapper:
    def __init__(
        self, func: ReducerType, skip_count=1, static_payload: Optional[dict] = None
    ):
        self._func = func
        self._has_payload = skip_count == 1
        self._static_payload = static_payload

        self._payload_type: Optional[Type[BaseModel]] = None
        if len(inspect.signature(func).parameters.values()) > 0:
            self._payload_type = list(inspect.signature(func).parameters.values())[
                0
            ].annotation

        self._state_type = list(inspect.signature(func).parameters.values())[
            skip_count
        ].annotation

    def __call__(self, *args) -> tuple[Union[tuple[Entity], Entity], Any]:
        return self._func(*args)

    def translate_payload(self, payload: Optional[Union[int, str, dict]]):
        if not self._has_payload:
            raise ValueError("no skip_count do not support payload translation")

        if self._static_payload:
            return copy.deepcopy(self._static_payload)

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
    def get_matching_reducer(self, action: Action) -> Optional[ComponentMethodWrapper]:
        ...

    @abstractmethod
    def get_matching_method_name(self, action: Action) -> Optional[str]:
        ...


class ConcreteActionRouter(ActionRouter):
    mappings: dict[str, ComponentMethodWrapper]
    method_mappings: dict[str, str]

    def is_enabled_action(self, action: Action) -> bool:
        mapping = self._find_mapping_name(action.signature, self.mappings)
        return mapping is not None

    def get_matching_reducer(self, action: Action) -> Optional[ComponentMethodWrapper]:
        mapping_name = self._find_mapping_name(action.signature, self.mappings)
        if mapping_name is None:
            return None
        return self.mappings[mapping_name]

    def get_matching_method_name(self, action: Action) -> Optional[str]:
        mapping_name = self._find_mapping_name(action.signature, self.method_mappings)
        if mapping_name is None:
            return None

        return self.method_mappings[mapping_name]

    def _find_mapping_name(self, target: str, mappings) -> Optional[str]:
        if target in mappings:
            return target

        for mapping_name in mappings:
            if mapping_name[0] == "$" and mapping_name.replace("$", "") in target:
                return cast(str, mapping_name)

        return None


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
            name: store.read_entity(address, default=self._default_state.get(name))
            for name, address in self._get_bound_names().items()
        }

        return state_type(**entities)

    def set_state(self, store: Store, state):
        bounded_names = self._get_bound_names()

        for name, entity in dict(state).items():
            if name in bounded_names:
                store.set_entity(bounded_names[name], entity)

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

    def init_store(self, store: Store):
        local_store = store.local(self._name)
        for name in self._default_state:
            local_store.read_entity(name, default=self._default_state[name])

    def __call__(self, action: Action, store: Store) -> list[Event]:
        if not self._action_router.is_enabled_action(action):
            return []

        local_store = store.local(self._name)

        reducer = self._action_router.get_matching_reducer(action)
        method_name = self._action_router.get_matching_method_name(action)

        if reducer is None or method_name is None:
            return []

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

        if all(event.tag not in (Tag.REJECT, Tag.ACCEPT) for event in events):
            return tagged_events + [
                Event(name=self._name, method=method_name, tag=Tag.ACCEPT, payload={})
            ]

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


class StaticPayloadReducerInfo(BaseModel):
    name: str
    payload: dict


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
    listening_actions: dict[str, Union[str, StaticPayloadReducerInfo]] = Field(
        default_factory=dict
    )
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
        dispatcher.init_store(environment.store)

        for view_name, view in self.get_views().items():
            environment.add_view(f"{self.name}.{view_name}", view)

    def get_action_router(self) -> ActionRouter:
        reducer_methods = self.get_every_reducer_methods()

        wild_card_mappings = {
            f"{WILD_CARD}.{method}": method for method in reducer_methods.keys()
        }
        default_mappings = {
            f"{self.name}.{method}": method for method in reducer_methods.keys()
        }
        reducer_mappings, method_mappings = {}, {}
        method_mappings.update(default_mappings)
        method_mappings.update(wild_card_mappings)

        # str-type reducers
        for listening_signature, reducer_info in self.listening_actions.items():
            if isinstance(reducer_info, str):
                method_mappings[listening_signature] = reducer_info

        reducer_mappings.update(
            {k: reducer_methods[v] for k, v in method_mappings.items()}
        )

        # StaticPayloadReducerInfo-type reducers
        for listening_signature, reducer_info in self.listening_actions.items():
            if isinstance(reducer_info, StaticPayloadReducerInfo):
                method_mappings[listening_signature] = reducer_info.name
                reducer_mappings[listening_signature] = self._get_reducer_method(
                    reducer_info.name,
                    reducer_info.payload,
                )

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

    def get_every_reducer_methods(self):
        return {
            method_name: self._get_reducer_method(method_name)
            for method_name in getattr(self, "__reducers__")
        }

    def _get_reducer_method(self, reducer_name, static_payload: Optional[dict] = None):
        return ComponentMethodWrapper(
            getattr(self, reducer_name), static_payload=static_payload
        )

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
