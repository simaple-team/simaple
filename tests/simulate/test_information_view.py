from simaple.core.base import ActionStat
from simaple.simulate.component.base import ReducerState
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import InformationParentView
from simaple.simulate.core.base import AddressedStore, ConcreteStore, Entity, ViewSet
from simaple.simulate.global_property import GlobalProperty


class SomeEntity(Entity):
    obj: int = 3


class SomeTestState(ReducerState):
    some_state: SomeEntity


class ViewTestComponent(SkillComponent):
    value: int = 5

    def get_default_state(self):
        return {"some_state": SomeEntity()}
