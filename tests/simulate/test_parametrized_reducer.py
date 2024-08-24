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
        return payload, [
            {"name": self.name, "payload": payload.model_dump(), "tag": None}
        ]


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
    engine = engine_builder.build_monotonic_engine()
    assert engine.resolve(
        dict(
            name="some_parametrized_action",
            method="use",
        )
    )[0][
        "payload"
    ] == {"value": 2}

    assert engine.resolve(
        dict(
            name="some_action",
            method="use",
            payload={"value": 1324},
        )
    )[0]["payload"] == {"value": 1324}
