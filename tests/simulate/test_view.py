from simaple.simulate.base import AddressedStore, ConcreteStore, Environment, State
from simaple.simulate.component.base import Component, view_method


class SomeState(State):
    obj: int = 3


class ViewTestComponent(Component):
    value: int = 5

    def get_default_state(self):
        return {"some_state": SomeState()}

    @view_method
    def naming(self, some_state):
        return str(some_state.obj + self.value)


def test_view():
    store = AddressedStore(ConcreteStore())
    environment = Environment(store=store)

    component = ViewTestComponent(name="test_component")
    component.add_to_environment(environment)

    assert environment.show("test_component.naming") == str(3 + 5)


def test_view_query():
    store = AddressedStore(ConcreteStore())
    environment = Environment(store=store)

    component = ViewTestComponent(name="test_component")
    component.add_to_environment(environment)

    view = environment.get_views(r".*\.naming")[0]
    assert view(environment.store) == str(3 + 5)
