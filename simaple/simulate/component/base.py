import inspect
from abc import abstractmethod
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union, cast

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import TypedDict

from simaple.core import Stat
from simaple.simulate.core import Action, ActionSignature, Event
from simaple.simulate.core.reducer import ReducerType, UnsafeReducer
from simaple.simulate.core.store import Store
from simaple.simulate.event import EventProvider, NamedEventProvider
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.reserved_names import Tag
from simaple.spec.loadable import TaggedNamespacedABCMeta

WILD_CARD = "*"

StateT = TypeVar("StateT")

ReducerPrecursorType = Callable[[Any, Any, StateT], tuple[StateT, list[Event]]]

ReducerPrecursorTypeT = TypeVar("ReducerPrecursorTypeT", bound=ReducerPrecursorType)
T = TypeVar("T", bound=BaseModel)


def reducer_method(func: ReducerPrecursorTypeT) -> ReducerPrecursorTypeT:
    func.__isreducer__ = True  # type: ignore

    return func


def view_method(func):
    func.__isview__ = True

    return func


class _ComponentAddon(
    BaseModel,
):
    """
    ComponentAddon is plug-and-play definition for inter-component communication.
    """

    model_config = ConfigDict(extra="forbid")

    when: str
    destination: str
    method: str
    payload: dict


def regularize_returned_event(
    maybe_events: Optional[Union[Event, list[Event]]]
) -> list[Event]:
    if maybe_events is None:
        return []

    if not isinstance(maybe_events, list):
        return [maybe_events]

    return maybe_events


def tag_events_by_method_name(
    owner_name: str, method_name: str, events: list[Event]
) -> list[Event]:
    tagged_events: list[Event] = []
    for event in events:
        tagged_event: Event = {
            "name": event["name"],
            "payload": event["payload"],
            "method": method_name,
            "tag": event["tag"] or method_name,
            "handler": event.get("handler", None),
        }
        tagged_events.append(tagged_event)

    if all(event["tag"] not in (Tag.REJECT, Tag.ACCEPT) for event in events):
        return tagged_events + [
            {
                "name": owner_name,
                "method": method_name,
                "tag": Tag.ACCEPT,
                "payload": {},
                "handler": None,
            }
        ]

    return tagged_events


def event_tagged_reducer(
    owner_name: str, method_name: str, event_provider: EventProvider
):
    def wrapper(reducer):
        @wraps(reducer)
        def wrapped(action: Action, store: Store) -> list[Event]:
            events = reducer(action, store)
            if len(events) == 0:
                return []

            if events[0]["name"] != owner_name:
                events = [event_provider.wrap_with_modifier(event) for event in events]
            return tag_events_by_method_name(owner_name, method_name, events)

        return wrapped

    return wrapper


def init_component_store(owner_name, default_state, store: Store):
    local_store = store.local(owner_name)
    for name in default_state:
        local_store.set_entity(name, default_state[name])


def view_use_store(store_name, bounded_stores: dict[str, str]):
    def wrapper(viewer):
        state_type = list(inspect.signature(viewer).parameters.values())[0].annotation

        @wraps(viewer)
        def wrapped(global_store: Store):
            local_store = global_store.local(store_name)

            my_entities = local_store.read(store_name)

            for name, address in bounded_stores.items():
                entity = local_store.read_entity(address, None)
                assert entity is not None
                my_entities[name] = entity

            state = state_type(**my_entities)

            view = viewer(state)
            return view

        return wrapped

    return wrapper


def _create_binding_with_store(
    owner_name: str,
    properties: list[str],
    bindings: dict[str, str],
):

    property_address = {}

    for property_name in properties:
        if property_name in bindings:
            property_address[property_name] = bindings[property_name]
        else:
            property_address[property_name] = f".{owner_name}.{property_name}"

    return property_address


def compile_into_unsafe_reducer(property_address: dict[str, str]):
    """
    address: mapping about {address: property_name}

    Returning reducer does not ensure no-op for invalid action.
    Create proper relation between action and reducer is responsible to caller.
    """

    def wrapper(component_method):
        payload_type = list(inspect.signature(component_method).parameters.values())[
            0
        ].annotation

        @wraps(component_method)
        def wrapped(action: Action, global_store: Store) -> list[Event]:
            # if no-op, return []
            state = {}

            for name, address in property_address.items():
                entity = global_store.read_entity(address, None)
                state[name] = entity

            payload = action["payload"]

            if payload_type not in (int, str, float, None):
                payload = payload_type(**action["payload"])

            output_state, maybe_events = component_method(payload, state)
            output_state_dict = dict(output_state)

            for name, address in property_address.items():
                global_store.set_entity(address, output_state_dict[name])

            return regularize_returned_event(maybe_events)

        return wrapped

    return wrapper


def no_op_reducer(action: Action, store: Store) -> list[Event]:
    return []


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


def _old_signature_to_new_signature(old_signature: str) -> ActionSignature:
    split = old_signature.split(".")

    return split[0], ".".join(split[1:])


class ComponentInformation(TypedDict):
    id: int
    name: str


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

    id: str
    name: str
    modifier: Optional[Stat] = None

    binds: dict[str, str] = Field(default_factory=dict)
    addons: list[_ComponentAddon] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def get_default_state(self) -> Any: ...

    @property
    def event_provider(self) -> EventProvider:
        return NamedEventProvider(self.name, self.modifier)

    def reducer(self, method_name: str) -> ReducerType:
        if method_name not in getattr(self, "__reducers__"):
            raise ValueError(f"Reducer {method_name} is not defined in {self.name}")

        bounded_stores = GlobalProperty.get_default_binds()
        bounded_stores.update(self.binds)

        # TODO: remove these lines with explicit state passing
        model_fields = list(self.get_default_state().keys())

        property_address = _create_binding_with_store(
            self.name,
            model_fields,
            bounded_stores,
        )

        return event_tagged_reducer(self.name, method_name, self.event_provider)(
            compile_into_unsafe_reducer(property_address)(getattr(self, method_name))
        )

    def get_unsafe_reducers(self) -> list[UnsafeReducer]:
        if len(getattr(self, "__reducers__")) == 0:
            return []

        bounded_stores = GlobalProperty.get_default_binds()
        bounded_stores.update(self.binds)

        # TODO: remove these lines with explicit state passing
        model_fields = list(self.get_default_state().keys())

        property_address = _create_binding_with_store(
            self.name,
            model_fields,
            bounded_stores,
        )

        return [
            {
                "reducer": event_tagged_reducer(
                    self.name, method_name, self.event_provider
                )(
                    compile_into_unsafe_reducer(property_address)(
                        getattr(self, method_name)
                    )
                ),
                "name": (self.name, method_name),
                "target_action_signature": [
                    (self.name, method_name),
                    (WILD_CARD, method_name),
                ],
            }
            for method_name in getattr(self, "__reducers__")
        ]

    def get_views(self):
        bounded_stores = GlobalProperty.get_default_binds()
        bounded_stores.update(self.binds)

        return {
            method_name: view_use_store(
                self.name,
                bounded_stores=bounded_stores,
            )(getattr(self, method_name))
            for method_name in getattr(self, "__views__")
        }

    @view_method
    def info(self, _: Any) -> ComponentInformation:
        return cast(ComponentInformation, self.model_dump())
