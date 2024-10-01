from simaple.simulate.component.base import ReducerState, reducer_method, view_method
from simaple.simulate.component.entity import Keydown, LastingStack
from simaple.simulate.component.skill import Cooldown, SkillComponent
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    KeydownSkillTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.util import is_rejected
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class FinalCutState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics


class FinalCutComponent(SkillComponent, UseSimpleAttackTrait, CooldownValidityTrait):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    sudden_raid_cooltime_reduce: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: FinalCutState):
        return self.elapse_simple_attack(time, state)

    @reducer_method
    def use(self, _: None, state: FinalCutState):
        return self.use_simple_attack(state)

    @reducer_method
    def sudden_raid(self, _: None, state: FinalCutState):
        state = state.deepcopy()
        state.cooldown.reduce_by_rate(self.sudden_raid_cooltime_reduce * 0.01)
        return state, []

    @view_method
    def validity(self, state: FinalCutState):
        return self.validity_in_cooldown_trait(state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit


class BladeStormState(ReducerState):
    cooldown: Cooldown
    keydown: Keydown
    dynamics: Dynamics


class BladeStormComponent(SkillComponent, KeydownSkillTrait, CooldownValidityTrait):
    maximum_keydown_time: float

    damage: float
    hit: float
    delay: float
    cooldown_duration: float

    keydown_prepare_delay: float
    keydown_end_delay: float

    prepare_damage: float
    prepare_hit: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "keydown": Keydown(interval=self.delay, running=False),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: BladeStormState,
    ):
        state, events = self.use_keydown_trait(state)

        if not is_rejected(events):
            events.append(
                self.event_provider.dealt(self.prepare_damage, self.prepare_hit)
            )

        return state, events

    @reducer_method
    def elapse(self, time: float, state: BladeStormState):
        state, events = self.elapse_keydown_trait(time, state)
        return state, events

    @reducer_method
    def stop(self, _, state: BladeStormState):
        state, events = self.stop_keydown_trait(state)
        return state, events

    @view_method
    def validity(self, state: BladeStormState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def keydown(self, state: BladeStormState):
        return self.keydown_view_in_keydown_trait(state)

    def _get_maximum_keydown_time_prepare_delay(self) -> tuple[float, float]:
        return self.maximum_keydown_time, self.keydown_prepare_delay

    def _get_keydown_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_keydown_end_damage_hit_delay(self) -> tuple[float, float, float]:
        return 0, 0, self.keydown_end_delay


class KarmaBladeTriggerState(ReducerState):
    cooldown: Cooldown
    lasting_stack: LastingStack
    dynamics: Dynamics


class KarmaBladeTriggerComponent(SkillComponent, CooldownValidityTrait):
    name: str
    damage: float
    hit: float
    delay: float
    triggable_count: int
    lasting_duration: float
    cooldown_duration: float

    finish_damage: float
    finish_hit: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting_stack": LastingStack(
                stack=0,
                maximum_stack=self.triggable_count,
                duration=self.lasting_duration,
            ),
        }

    @reducer_method
    def elapse(self, time: float, state: KarmaBladeTriggerState):
        state = state.deepcopy()
        state.cooldown.elapse(time)

        was_running = state.lasting_stack.enabled()
        state.lasting_stack.elapse(time)

        if was_running and not state.lasting_stack.enabled():
            state.lasting_stack.reset()
            return (
                state,
                [self.event_provider.dealt(self.finish_damage, self.finish_hit)],
            )

        return state, []

    @reducer_method
    def use(self, _: None, state: KarmaBladeTriggerState):
        state = state.deepcopy()
        state.lasting_stack.reset()
        state.lasting_stack.increase(self.triggable_count)
        return state, []

    @reducer_method
    def trigger(self, _: None, state: KarmaBladeTriggerState):
        if not state.lasting_stack.enabled():
            return state, []
        if not state.cooldown.available:
            return state, []

        state = state.deepcopy()
        state.cooldown.set_time_left(self.cooldown_duration)
        state.lasting_stack.decrease(1)

        if state.lasting_stack.stack <= 0:
            state.lasting_stack.reset()
            return (
                state,
                [
                    self.event_provider.dealt(self.damage, self.hit),
                    self.event_provider.dealt(self.finish_damage, self.finish_hit),
                ],
            )

        return (
            state,
            [self.event_provider.dealt(self.damage, self.hit)],
        )

    @view_method
    def validity(self, state: KarmaBladeTriggerState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: KarmaBladeTriggerState):
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.lasting_stack.time_left,
            lasting_duration=self.lasting_duration,
            stack=state.lasting_stack.stack,
        )
