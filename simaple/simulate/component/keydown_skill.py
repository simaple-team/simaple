from simaple.simulate.component.base import (
    Entity,
    ReducerState,
    reducer_method,
    view_method,
)
from simaple.simulate.component.entity import CooldownState
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Validity
from simaple.simulate.global_property import Dynamics


class KeydownState(Entity):
    time_elapsed_after_latest_action: float = 999_999_999
    time_elapsed_after_first_action: float = 999_999_999
    running: bool

    def start(self):
        self.time_elapsed_after_latest_action = 0.0
        self.time_elapsed_after_first_action = 0.0
        self.running = True

    def will_keydown_lasts(self, time, maximum_keydown_time: float = 999_999_999):
        return (self.time_elapsed_after_first_action + time) <= maximum_keydown_time

    def stop(self):
        self.running = False

    def is_running(self) -> bool:
        return self.running

    def continue_running(self):
        self.time_elapsed_after_latest_action = 0.0

    def elapse(self, time, allowed_interval, maximum_keydown_time):
        self.time_elapsed_after_latest_action += time
        self.time_elapsed_after_first_action += time

        if self.time_elapsed_after_first_action > maximum_keydown_time:
            self.stop()
        elif self.is_running() and self._can_continue_keydown(allowed_interval):
            return
        else:
            self.stop()

    def _can_continue_keydown(self, allowed_interval: float) -> bool:
        return self.time_elapsed_after_latest_action <= allowed_interval


class KeydownSkillState(ReducerState):
    cooldown_state: CooldownState
    keydown_state: KeydownState
    dynamics: Dynamics


class KeydownSkillComponent(SkillComponent):
    maximum_keydown_time: float = 999_999_999

    damage: float
    hit: float
    delay: float
    cooldown: float = 0.0

    keydown_end_delay: float = 0.0

    finish_damage: float = 0.0
    finish_hit: float = 0.0

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "keydown_state": KeydownState(running=False),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: KeydownSkillState,
    ):
        state = state.copy()

        if not state.cooldown_state.available:
            return state, self.event_provider.rejected()

        damage_event = [self.event_provider.dealt(self.damage, self.hit)]
        delay_event = [self.event_provider.delayed(self.delay)]

        # check user's trigger
        if not state.keydown_state.is_running():
            state.keydown_state.start()

        # if keydown will end by trigger this action
        if not state.keydown_state.will_keydown_lasts(
            self.delay, self.maximum_keydown_time
        ):
            # apply cooldown and finisher
            state.keydown_state.stop()
            state.cooldown_state.set_time_left(
                state.dynamics.stat.calculate_cooldown(self.cooldown)
            )
            damage_event.append(
                self.event_provider.dealt(self.finish_damage, self.finish_hit)
            )
            delay_event.append(self.event_provider.delayed(self.keydown_end_delay))
        else:
            state.keydown_state.continue_running()

        return state, damage_event + delay_event

    @reducer_method
    def elapse(self, time: float, state: KeydownSkillState):
        state = state.copy()

        state.cooldown_state.elapse(time)
        was_running = state.keydown_state.is_running()
        state.keydown_state.elapse(time, self.delay, self.maximum_keydown_time)

        events = [self.event_provider.elapsed(time)]

        if was_running and not state.keydown_state.is_running():
            state.cooldown_state.set_time_left(
                state.dynamics.stat.calculate_cooldown(self.cooldown)
            )

            # if keydown stopped and finish delay is not zero, compensate un-resolved delay.
            if self.keydown_end_delay > time:
                events.append(
                    self.event_provider.delayed(self.keydown_end_delay - time)
                )
                state.cooldown_state.elapse(self.keydown_end_delay - time)

        return state, events

    @view_method
    def validity(self, state: KeydownSkillState):
        return Validity(
            name=self.name,
            time_left=max(0, state.cooldown_state.time_left),
            valid=state.cooldown_state.available,
            cooldown=self.cooldown,
        )
