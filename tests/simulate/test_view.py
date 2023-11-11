from simaple.core.base import ActionStat
from simaple.simulate.base import AddressedStore, ConcreteStore, Entity, Environment
from simaple.simulate.component.base import Component, ReducerState, view_method
from simaple.simulate.global_property import GlobalProperty


class SomeEntity(Entity):
    obj: int = 3


class SomeTestState(ReducerState):
    some_state: SomeEntity


class ViewTestComponent(Component):
    value: int = 5

    def get_default_state(self):
        return {"some_state": SomeEntity()}

    @view_method
    def naming(self, state: SomeTestState):
        return str(state.some_state.obj + self.value)


def test_view():
    store = AddressedStore(ConcreteStore())
    global_property = GlobalProperty(ActionStat())
    global_property.install_global_properties(store)

    environment = Environment(store=store)

    component = ViewTestComponent(id="dummy", name="test_component")
    component.add_to_environment(environment)

    assert environment.show("test_component.naming") == str(3 + 5)


def test_view_query():
    store = AddressedStore(ConcreteStore())
    global_property = GlobalProperty(ActionStat())
    global_property.install_global_properties(store)

    environment = Environment(store=store)

    component = ViewTestComponent(id="dummy", name="test_component")
    component.add_to_environment(environment)

    view = environment.get_views(r".*\.naming")[0]
    assert view(environment._store) == str(3 + 5)
