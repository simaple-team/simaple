from simaple.simulate.base import AddressedStore, ConcreteStore, Environment, State
from simaple.simulate.component.base import Component, view_method
from simaple.simulate.component.view import Validity, ValidityParentView


class SomeState(State):
    obj: int = 3


class ViewTestComponent(Component):
    value: int = 5

    def get_default_state(self):
        return {"some_state": SomeState()}

    @view_method
    def naming(self, some_state):
        return str(some_state.obj + self.value)

    @view_method
    def validity(self, some_state):
        return Validity(name=self.name, time_left=12, valid=False)


def test_view():
    store = AddressedStore(ConcreteStore())
    environment = Environment(store=store)

    component = ViewTestComponent(name="test_component")
    component.add_to_environment(environment)

    ValidityParentView.build_and_install(environment, "validity")

    assert environment.show("validity") == [
        Validity(name="test_component", time_left=12.0, valid=False)
    ]
