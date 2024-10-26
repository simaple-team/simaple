from collections import defaultdict

from simaple.simulate.component.base import Component, init_component_store
from simaple.simulate.core.action import Action, get_action_signature
from simaple.simulate.core.reducer import ReducerType
from simaple.simulate.core.store import Store
from simaple.simulate.core.view import View, ViewSet
from simaple.simulate.engine import BasicOperationEngine, OperationEngine
from simaple.simulate.policy import get_operation_handlers


class Usecase:
    def __init__(self):
        self._listeners: dict[tuple[str, str], list[ReducerType]] = defaultdict(list)
        self._views: dict[str, View] = {}
        self._initial_states: dict[str, dict] = {}

    def initial_state(self, name: str, initial_state):
        self._initial_states[name] = initial_state

    def listen(self, action: tuple[str, str], reducer: ReducerType):
        self._listeners[action].append(reducer)

    def add_view(self, view_name: str, view: View):
        self._views[view_name] = view

    def build_root_reducer(self) -> ReducerType:
        listeners = self._listeners

        def root_reducer(action: Action, store: Store):
            action_signature = get_action_signature(action)
            events = []

            for reducer in listeners[action_signature]:
                events.extend(reducer(action, store))

            return events

        return root_reducer

    def build_viewset(self) -> ViewSet:
        viewers = self._views
        viewset = ViewSet()

        for view_name, viewer in viewers.items():
            viewset.add_view(view_name, viewer)

        return viewset

    def use_component(self, component: Component):
        unsafe_reducers = component.get_unsafe_reducers()
        for unsafe_reducer in unsafe_reducers:
            for action_signature in unsafe_reducer["target_action_signature"]:
                self.listen(action_signature, unsafe_reducer["reducer"])

        for view_name, view in component.get_views().items():
            self.add_view(f"{component.name}.{view_name}", view)

        self.initial_state(component.name, component.get_default_state())

    def create_engine(self, store) -> OperationEngine:
        for initial_state_name, initial_state in self._initial_states.items():
            init_component_store(initial_state_name, initial_state, store)

        return BasicOperationEngine(
            self.build_root_reducer(),
            store,
            self.build_viewset(),
            get_operation_handlers(),
        )
