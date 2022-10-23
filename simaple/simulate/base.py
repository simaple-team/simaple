import inspect
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, List, Optional

from pydantic import BaseModel, Extra

from simaple.spec.loadable import TaggedNamespacedABCMeta


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
    def signature(self):
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
    def signature(self):
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

    def dispatch(self, event: Event) -> Optional[Action]:
        if event.signature in self.allowed_signatures:
            return self._action.copy()

        return None


class Store(metaclass=ABCMeta):
    def use_state(self, name: str, default: State = None):
        return self.read_state(name, default=default), self.set_state

    @abstractmethod
    def read_state(self, name: str, default: State = None):
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

    def handle(self, event: Event) -> List[Action]:
        ...


class Reducer:
    def __init__(self, store: AddressedStore):
        self.dispatchers = {}
        self.store = store

    def add_reducer(
        self, signature: str, dispatcher: Callable[[Action, Store], tuple[list[Event]]]
    ):
        self.dispatchers[signature] = dispatcher

    def resolve(self, action: Action) -> list[Event]:
        local_store = self.store.local(action.name)
        return self.dispatchers[action.signature](action, local_store)


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


def component_view(func):
    func.__component_view__ = True
    return func


class ComponentMetaclass(TaggedNamespacedABCMeta("component")):
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

    class Config:
        extra = Extra.forbid
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    @abstractmethod
    def get_default_state(self) -> dict[str, State]:
        ...

    def get_dispatchers(self):
        return getattr(self, "__dispatchers__")

    def event(self, tag=None) -> Event:
        return Event(
            name=self.name,
            tag=tag,
        )

    def add_to_reducer(self, reducer: Reducer):
        for method_name in self.get_dispatchers():
            reducer.add_reducer(f"{self.name}.{method_name}", self.dispatch)

    def dispatch(self, action: Action, store: Store) -> List[Event]:
        default_state = self.get_default_state()
        dispatcher = getattr(self, action.method)

        input_states = dispatcher.get_states(store, default_state)
        output_states, events = dispatcher(action.payload, *input_states)
        if not isinstance(output_states, tuple):
            output_states = (output_states,)
        dispatcher.set_states(store, output_states)

        if events is None:
            return []

        if isinstance(events, Event):
            events = [events]

        for event in events:
            event.method = action.method
            if event.tag is None:
                event.tag = action.method

        return events


class Container:
    components: list[Component]

    def subscribe(self, store: Store):
        for component in self.components:
            component.subscribe(store)


class View(metaclass=ABCMeta):
    @abstractmethod
    def aggregate(self, components):
        ...
