from typing import Optional, Type

from simaple.simulate.component.base import (
    Component,
    init_component_store,
    listening_actions_to_listeners,
)
from simaple.simulate.core.reducer import (
    Listener,
    ReducerPrecursor,
    ReducerType,
    create_safe_reducer,
    listener_to_reducer_precursor,
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

        self._reducer_precursors: list[ReducerPrecursor] = []
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
        reducer_precursor_from_listeners = [
            listener_to_reducer_precursor(listener, self._reducer_precursors)
            for listener in self._listeners
        ]
        return sum_reducers(
            [
                create_safe_reducer(
                    self._reducer_precursors + reducer_precursor_from_listeners
                )
            ]
            + self._reducers
        )

    def add_reducer(self, reducer, store_initializer=None) -> "EngineBuilder":
        self._reducers.append(reducer)
        if store_initializer:
            store_initializer(self._store)

        return self

    def add_component(self, component: Component) -> "EngineBuilder":
        init_component_store(component.name, component.get_default_state(), self._store)

        precursors = component.get_reducer_precursors()
        listeners = listening_actions_to_listeners(
            component.name, component.listening_actions
        )

        self._reducer_precursors += precursors
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
