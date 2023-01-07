from simaple.core.base import Stat
from simaple.simulate.base import Entity, Event
from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import (
    Cooldown,
    Cycle,
    Lasting,
    LastingStack,
    Stack,
)
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    AddDOTDamageTrait,
    BuffTrait,
    InvalidatableCooldownTrait,
    PeriodicWithSimpleDamageTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.global_property import Dynamics


class ElysionState(ReducerState):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics
    stack: LastingStack
    crack_cooldown: Cooldown


class Elysion(SkillComponent, BuffTrait, InvalidatableCooldownTrait):
    cooldown_duration: float
    delay: float
    lasting_duration: float

    crack_damage: float
    crack_hit: int
    crack_cooldown: float
    crack_duration: float
    maximum_crack_count: int

    def get_default_state(self) -> dict[str, Entity]:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "stack": LastingStack(
                maximum_stack=self.maximum_crack_count, duration=self.crack_duration
            ),
            "crack_cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def crack(self, _: None, state: ElysionState):
        if not state.lasting.enabled() or not state.crack_cooldown.available:
            return state, []

        state = state.deepcopy()
        state.stack.increase()
        if state.stack.is_maximum():
            state.stack.reset()
            state.crack_cooldown.set_time_left(self.crack_cooldown)
            return state, [self.event_provider.dealt(self.crack_damage, self.crack_hit)]

        return state, []

    @reducer_method
    def elapse(self, time: float, state: ElysionState):
        state = state.deepcopy()

        state.cooldown.elapse(time)
        state.lasting.elapse(time)
        state.crack_cooldown.elapse(time)
        state.stack.elapse(time)

        return state, [
            self.event_provider.elapsed(time),
        ]

    @reducer_method
    def use(self, _: None, state: ElysionState):
        return self.use_buff_trait(state)

    @view_method
    def running(self, state: ElysionState) -> Running:
        return self.running_in_buff_trait(state)

    def _get_lasting_duration(self, state: ElysionState) -> float:
        return self.lasting_duration
