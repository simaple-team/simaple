from typing import Optional, Type

from simaple.simulate.base import (
    AddressedStore,
    ConcreteStore,
    Dispatcher,
    RouterDispatcher,
    View,
    ViewSet,
)
from simaple.simulate.component.base import Component
from simaple.simulate.engine import MonotonicEngine, OperationEngine
from simaple.simulate.policy import get_operation_handlers
from simaple.simulate.view import AggregationView


class EngineBuilder:
    def __init__(self, store: Optional[AddressedStore] = None) -> None:
        self._router = RouterDispatcher()
        self._viewset: ViewSet = ViewSet()
        if store is None:
            self._store: AddressedStore = AddressedStore(ConcreteStore())
        else:
            self._store = store

    def build_monotonic_engine(self) -> MonotonicEngine:
        return MonotonicEngine(
            router=self._router,
            store=self._store,
            viewset=self._viewset,
        )

    def build_operation_engine(self) -> OperationEngine:
        return OperationEngine(
            self._router,
            self._store,
            self._viewset,
            get_operation_handlers(),
        )

    def add_dispatcher(self, dispatcher: Dispatcher) -> "EngineBuilder":
        self._router.install(dispatcher)
        dispatcher.init_store(self._store)  # TODO: remove this

        return self

    def add_component(self, component: Component) -> "EngineBuilder":
        dispatcher = component.export_dispatcher()
        self.add_dispatcher(dispatcher)

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
