from typing import TypedDict

from simaple.core.base import ActionStat
from simaple.simulate.component.base import Component, view_method
from simaple.simulate.core.base import Entity
from simaple.simulate.core.store import AddressedStore, ConcreteStore
from simaple.simulate.global_property import GlobalProperty
from simaple.simulate.usecase import Usecase


class SomeEntity(Entity):
    obj: int = 3


class SomeTestState(TypedDict):
    some_state: SomeEntity


class ViewTestComponent(Component):
    value: int = 5

    def get_default_state(self) -> SomeTestState:
        return {"some_state": SomeEntity()}

    @view_method
    def naming(self, state: SomeTestState):
        return str(state["some_state"].obj + self.value)


def test_view():
    store = AddressedStore(ConcreteStore())
    global_property = GlobalProperty(ActionStat())
    global_property.install_global_properties(store)

    usecase = Usecase()
    usecase.use_component(ViewTestComponent(id="dummy", name="test_component"))

    runtime = usecase.create_simulation_runtime(store=store)

    assert runtime.get_viewer()("test_component.naming") == str(3 + 5)
