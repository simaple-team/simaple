from simaple.core.base import ActionStat
from simaple.simulate.base import AddressedStore, ConcreteStore, Entity, ViewSet
from simaple.simulate.component.base import ReducerState
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import InformationParentView
from simaple.simulate.global_property import GlobalProperty


class SomeEntity(Entity):
    obj: int = 3


class SomeTestState(ReducerState):
    some_state: SomeEntity


class ViewTestComponent(SkillComponent):
    value: int = 5

    def get_default_state(self):
        return {"some_state": SomeEntity()}


def test_view():
    store = AddressedStore(ConcreteStore())
    global_property = GlobalProperty(ActionStat())
    global_property.install_global_properties(store)
    viewset = ViewSet()

    component = ViewTestComponent(name="test_component", delay=0, cooldown_duration=0, id="test")

    for view_name, view in component.get_views().items():
        viewset.add_view(f"{component.name}.{view_name}", view)

    component.export_dispatcher().init_store(store)
    viewset.add_view("info", InformationParentView.build(viewset))

    assert viewset.show("info", store) == [
        {
            "id": "test",
            "name": "test_component",
            "listening_actions": {},
            "binds": {"dynamics": "global.dynamics"},
            "disable_validity": False,
            "modifier": None,
            "cooldown_duration": 0.0,
            "delay": 0.0,
            "value": 5,
        },
    ]
