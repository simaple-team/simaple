from typing import Optional, Type

from simaple.simulate.base import (
    AddressedStore,
    Client,
    ConcreteStore,
    Dispatcher,
    RouterDispatcher,
    View,
    ViewSet,
)
from simaple.simulate.component.base import Component
from simaple.simulate.view import AggregationView


class ClientBuilder:
    def __init__(self, store: Optional[AddressedStore] = None) -> None:
        self._router = RouterDispatcher()
        self._viewset: ViewSet = ViewSet()
        if store is None:
            self._store: AddressedStore = AddressedStore(ConcreteStore())
        else:
            self._store = store

    def build_client(self) -> Client:
        return Client(
            router=self._router,
            store=self._store,
            viewset=self._viewset,
        )

    def add_dispatcher(self, dispatcher: Dispatcher) -> "ClientBuilder":
        self._router.install(dispatcher)
        dispatcher.init_store(self._store)  # TODO: remove this

        return self

    def add_component(self, component: Component) -> "ClientBuilder":
        dispatcher = component.export_dispatcher()
        self.add_dispatcher(dispatcher)

        for view_name, view in component.get_views().items():
            self._viewset.add_view(f"{component.name}.{view_name}", view)

        return self

    def add_view(self, name: str, view: View) -> "ClientBuilder":
        self._viewset.add_view(name, view)

        return self

    def add_aggregation_view(
        self, aggregation_view: Type[AggregationView], name: str
    ) -> "ClientBuilder":
        view = aggregation_view.build(self._viewset)  # TODO: remove this (too slow)
        self._viewset.add_view(name, view)

        return self
