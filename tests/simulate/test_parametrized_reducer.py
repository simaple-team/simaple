from simaple.core.base import ActionStat
from simaple.simulate.base import (
    Action,
    AddressedStore,
    ConcreteStore,
    Entity,
    Environment,
    Event,
)
from simaple.simulate.component.base import Component, ReducerState, reducer_method
from simaple.simulate.global_property import GlobalProperty


class SomeEntity(Entity):
    obj: int = 3


class SomeTestState(ReducerState):
    some_state: SomeEntity


class ViewTestComponent(Component):
    value: int = 5

    def get_default_state(self):
        return {"some_state": SomeEntity()}

    @reducer_method
    def some_reducer(self, payload: None, state: SomeTestState):
        return payload, [Event(name=self.name, payload=payload)]


def test_paramterizd_reducer():
    store = AddressedStore(ConcreteStore())
    global_property = GlobalProperty(ActionStat())
    global_property.install_global_properties(store)

    environment = Environment(store=store)

    component = ViewTestComponent(
        id="dummy",
        name="test_component",
        listening_actions={
            "some_action.use": "some_reducer",
            "some_parametrized_action.use": {"name": "some_reducer", "payload": {3: 5}},
        },
    )

    component.add_to_environment(environment)

    assert environment.resolve(
        Action(
            name="some_parametrized_action",
            method="use",
            payload={"value": 1324},
        )
    )[0].payload == {3: 5}

    assert environment.resolve(
        Action(
            name="some_action",
            method="use",
            payload={"value": 1324},
        )
    )[0].payload == {"value": 1324}
