from simaple.simulate.component.base import ReducerState
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.core.store import Entity


class SomeEntity(Entity):
    obj: int = 3


class SomeTestState(ReducerState):
    some_state: SomeEntity


class ViewTestComponent(SkillComponent):
    value: int = 5

    def get_default_state(self):
        return {"some_state": SomeEntity()}
