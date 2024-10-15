from typing import Optional, Type

from simaple.simulate.component.base import (
    Component,
    init_component_store,
    listening_actions_to_listeners,
)
from simaple.simulate.core.reducer import (
    Listener,
    ReducerType,
    UnsafeReducer,
    create_safe_reducer,
    listener_to_unsafe_reducer,
    sum_reducers,
)
from simaple.simulate.core.runtime import SimulationRuntime
from simaple.simulate.core.store import AddressedStore, ConcreteStore
from simaple.simulate.core.view import View, ViewSet
from simaple.simulate.engine import BasicOperationEngine, OperationEngine
from simaple.simulate.policy import get_operation_handlers
from simaple.simulate.view import AggregationView


class EngineBuilder:
    def __init__(self, store: Optional[AddressedStore] = None) -> None:
        self._viewset: ViewSet = ViewSet()

        self._reducers: list[ReducerType] = []

        self._unsafe_reducers: list[UnsafeReducer] = []
        self._listeners: list[Listener] = []

        if store is None:
            self._store: AddressedStore = AddressedStore(ConcreteStore())
        else:
            self._store = store

    def build_simulation_runtime(self) -> SimulationRuntime:
        return SimulationRuntime(
            reducer=self.build_root_reducer(),
            store=self._store,
            viewset=self._viewset,
        )

    def build_operation_engine(self) -> OperationEngine:
        return BasicOperationEngine(
            self.build_root_reducer(),
            self._store,
            self._viewset,
            get_operation_handlers(),
        )

    def build_root_reducer(self) -> ReducerType:
        unsafe_reducer_from_listeners = [
            listener_to_unsafe_reducer(listener, self._unsafe_reducers)
            for listener in self._listeners
        ]
        return sum_reducers(
            [create_safe_reducer(self._unsafe_reducers + unsafe_reducer_from_listeners)]
            + self._reducers
        )

    def add_reducer(self, reducer, store_initializer=None) -> "EngineBuilder":
        self._reducers.append(reducer)
        if store_initializer:
            store_initializer(self._store)

        return self

    def add_component(self, component: Component) -> "EngineBuilder":
        init_component_store(component.name, component.get_default_state(), self._store)

        unsafe_reducers = component.get_unsafe_reducers()
        listeners = listening_actions_to_listeners(
            component.name, component.listening_actions
        )

        self._unsafe_reducers += unsafe_reducers
        self._listeners += listeners

        for view_name, view in component.get_views().items():
            self._viewset.add_view(f"{component.name}.{view_name}", view)

        return self

    def add_view(self, name: str, view: View) -> "EngineBuilder":
        self._viewset.add_view(name, view)

        return self

    def add_aggregation_view(
        self, aggregation_view: Type[AggregationView], name: str
    ) -> "EngineBuilder":
        view = aggregation_view.build(self._viewset)  # TODO: remove this (too slow)
        self._viewset.add_view(name, view)

        return self
