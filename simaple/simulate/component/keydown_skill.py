from simaple.simulate.component.base import State, reducer_method, view_method
from simaple.simulate.component.skill import CooldownState, SkillComponent
from simaple.simulate.component.view import Validity
from simaple.simulate.global_property import Dynamics


class KeydownState(State):
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
        cooldown_state: CooldownState,
        keydown_state: KeydownState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()
        keydown_state = keydown_state.copy()

        if not cooldown_state.available:
            return (cooldown_state, keydown_state), self.event_provider.rejected()

        damage_event = [self.event_provider.dealt(self.damage, self.hit)]
        delay_event = [self.event_provider.delayed(self.delay)]

        # check user's trigger
        if not keydown_state.is_running():
            keydown_state.start()

        # if keydown will end by trigger this action
        if not keydown_state.will_keydown_lasts(self.delay, self.maximum_keydown_time):
            # apply cooldown and finisher
            keydown_state.stop()
            cooldown_state.set_time_left(
                dynamics.stat.calculate_cooldown(self.cooldown)
            )
            damage_event.append(
                self.event_provider.dealt(self.finish_damage, self.finish_hit)
            )
            delay_event.append(self.event_provider.delayed(self.keydown_end_delay))
        else:
            keydown_state.continue_running()

        return (cooldown_state, keydown_state, dynamics), damage_event + delay_event

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        keydown_state: KeydownState,
        dynamics: Dynamics,
    ):
        cooldown_state, keydown_state = cooldown_state.copy(), keydown_state.copy()

        cooldown_state.elapse(time)
        was_running = keydown_state.is_running()
        keydown_state.elapse(time, self.delay, self.maximum_keydown_time)

        events = [self.event_provider.elapsed(time)]

        if was_running and not keydown_state.is_running():
            cooldown_state.set_time_left(
                dynamics.stat.calculate_cooldown(self.cooldown)
            )

            # if keydown stopped and finish delay is not zero, compensate un-resolved delay.
            if self.keydown_end_delay > time:
                events.append(
                    self.event_provider.delayed(self.keydown_end_delay - time)
                )
                cooldown_state.elapse(self.keydown_end_delay - time)

        return (cooldown_state, keydown_state, dynamics), events

    @view_method
    def validity(self, cooldown_state):
        return Validity(
            name=self.name,
            time_left=max(0, cooldown_state.time_left),
            valid=cooldown_state.available,
        )
