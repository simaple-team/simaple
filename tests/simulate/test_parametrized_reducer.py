from pydantic import BaseModel

from simaple.core.base import ActionStat
from simaple.simulate.base import AddressedStore, ConcreteStore, Entity
from simaple.simulate.builder import EngineBuilder
from simaple.simulate.component.base import Component, ReducerState, reducer_method
from simaple.simulate.global_property import GlobalProperty


class SomeEntity(Entity):
    obj: int = 3


class ViewTestPayload(BaseModel):
    value: int


class SomeTestState(ReducerState):
    some_state: SomeEntity


class ViewTestComponent(Component):
    value: int = 5

    def get_default_state(self):
        return {"some_state": SomeEntity()}

    @reducer_method
    def some_reducer(self, payload: ViewTestPayload, state: SomeTestState):
        return state, [
            {"name": self.name, "payload": payload.model_dump(), "tag": None}
        ]

    @reducer_method
    def use(self, _: None, state: SomeTestState):
        return state, [{"name": self.name, "payload": {}, "tag": "use"}]


def test_paramterizd_reducer():
    store = AddressedStore(ConcreteStore())
    global_property = GlobalProperty(ActionStat())
    global_property.install_global_properties(store)

    engine_builder = EngineBuilder(store=store)

    component = ViewTestComponent(
        id="dummy",
        name="test_component",
        listening_actions={
            "some_action.use": "some_reducer",
            "some_parametrized_action.use": {
                "name": "some_reducer",
                "payload": {"value": 2},
            },
        },
    )
    engine_builder.add_component(component)
    simulation_runtime = engine_builder.build_simulation_runtime()
    assert simulation_runtime.resolve(
        {"name": "some_parametrized_action", "method": "use", "payload": None}
    )[0]["payload"] == {"value": 2}

    assert simulation_runtime.resolve(
        {
            "name": "some_action",
            "method": "use",
            "payload": {"value": 1324},
        }
    )[0]["payload"] == {"value": 1324}


def test_addon():
    store = AddressedStore(ConcreteStore())
    global_property = GlobalProperty(ActionStat())
    global_property.install_global_properties(store)

    engine_builder = EngineBuilder(store=store)

    component_a = ViewTestComponent(
        id="dummy",
        name="component_a",
        addons=[
            {
                "when": "use",
                "destination": "component_b",
                "method": "some_reducer",
                "payload": {"value": 1324},
            }
        ],
    )

    component_b = ViewTestComponent(
        id="dummy",
        name="component_b",
    )

    engine_builder.add_component(component_a)
    engine_builder.add_component(component_b)

    simulation_runtime = engine_builder.build_simulation_runtime()
    assert simulation_runtime.resolve(
        {"name": "component_b", "method": "some_reducer", "payload": {"value": 100}}
    )[0] == {
        "name": "component_b",
        "payload": {"value": 100},
        "method": "some_reducer",
        "tag": "some_reducer",
        "handler": None,
    }

    assert simulation_runtime.resolve(
        {
            "name": "component_a",
            "method": "use",
            "payload": None,
        }
    ) == [
        {
            "name": "component_a",
            "payload": {},
            "method": "use",
            "tag": "use",
            "handler": None,
        },
        {
            "name": "component_a",
            "method": "use",
            "tag": "global.accept",
            "payload": {},
            "handler": None,
        },
        {
            "name": "component_b",
            "payload": {"value": 1324},
            "method": "some_reducer",
            "tag": "some_reducer",
            "handler": None,
        },
        {
            "name": "component_b",
            "method": "some_reducer",
            "tag": "global.accept",
            "payload": {},
            "handler": None,
        },
    ]
