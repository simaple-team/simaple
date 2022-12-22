from simaple.simulate.component.state import CooldownState, DurationState, IntervalState
from simaple.simulate.component.trait.base import (
    CooldownTrait,
    DelayTrait,
    DurationTrait,
    EventProviderTrait,
    InvalidatableTrait,
    NamedTrait,
    SimpleDamageTrait,
    TickDamageTrait,
)
from simaple.simulate.component.view import Validity
from simaple.simulate.global_property import Dynamics


class CooldownValidityTrait(CooldownTrait, NamedTrait):
    def validity_in_cooldown_trait(self, cooldown_state) -> Validity:
        return Validity(
            name=self._get_name(),
            time_left=max(0, cooldown_state.time_left),
            valid=cooldown_state.available,
            cooldown=self._get_cooldown(),
        )


class InvalidatableCooldownTrait(CooldownTrait, InvalidatableTrait, NamedTrait):
    def validity_in_invalidatable_cooldown_trait(
        self, cooldown_state: CooldownState
    ) -> Validity:
        return self.invalidate_if_disabled(
            Validity(
                name=self._get_name(),
                time_left=max(0, cooldown_state.time_left),
                valid=cooldown_state.available,
                cooldown=self._get_cooldown(),
            )
        )


class UseSimpleAttackTrait(
    CooldownTrait, SimpleDamageTrait, EventProviderTrait, DelayTrait
):
    def use_simple_attack(self, cooldown_state: CooldownState, dynamics: Dynamics):
        cooldown_state = cooldown_state.copy()

        if not cooldown_state.available:
            return (cooldown_state, dynamics), self.event_provider.rejected()

        cooldown_state.set_time_left(
            dynamics.stat.calculate_cooldown(self._get_cooldown())
        )

        damage, hit = self._get_simple_damage_hit()
        delay = self._get_delay()

        return (cooldown_state, dynamics), [
            self.event_provider.dealt(damage, hit),
            self.event_provider.delayed(delay),
        ]

    def elapse_simple_attack(self, time: float, cooldown_state: CooldownState):
        cooldown_state = cooldown_state.copy()
        cooldown_state.elapse(time)
        return cooldown_state, self.event_provider.elapsed(time)

    def use_multiple_damage(
        self, cooldown_state: CooldownState, dynamics: Dynamics, multiple: int
    ):
        cooldown_state = cooldown_state.copy()

        if not cooldown_state.available:
            return (cooldown_state, dynamics), self.event_provider.rejected()

        cooldown_state.set_time_left(
            dynamics.stat.calculate_cooldown(self._get_cooldown())
        )

        damage, hit = self._get_simple_damage_hit()
        delay = self._get_delay()

        return (cooldown_state, dynamics), [
            self.event_provider.dealt(damage, hit) for _ in range(multiple)
        ] + [self.event_provider.delayed(delay)]


class DurableTrait(CooldownTrait, DurationTrait, EventProviderTrait, DelayTrait):
    def use_durable_trait(
        self,
        cooldown_state: CooldownState,
        duration_state: DurationState,
        dynamics: Dynamics,
        duration_multiplier=1.0,
    ):
        cooldown_state = cooldown_state.copy()
        duration_state = duration_state.copy()

        if not cooldown_state.available:
            return (
                cooldown_state,
                duration_state,
                dynamics,
            ), self.event_provider.rejected()

        cooldown_state.set_time_left(
            dynamics.stat.calculate_cooldown(self._get_cooldown())
        )

        duration_state.set_time_left(
            dynamics.stat.calculate_buff_duration(
                self._get_duration() * duration_multiplier
            )
        )

        return (cooldown_state, duration_state, dynamics), self.event_provider.delayed(
            self._get_delay()
        )

    def elapse_durable_trait(
        self, time: float, cooldown_state: CooldownState, duration_state: DurationState
    ):
        cooldown_state = cooldown_state.copy()
        duration_state = duration_state.copy()

        cooldown_state.elapse(time)
        duration_state.elapse(time)

        return (cooldown_state, duration_state), [
            self.event_provider.elapsed(time),
        ]


class TickEmittingTrait(
    CooldownTrait,
    TickDamageTrait,
    SimpleDamageTrait,
    DurationTrait,
    EventProviderTrait,
    DelayTrait,
):
    def elapse_tick_emitting_trait(
        self, time: float, cooldown_state: CooldownState, interval_state: IntervalState
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        cooldown_state.elapse(time)
        lapse_count = interval_state.elapse(time)

        tick_damage, tick_hit = self._get_tick_damage_hit()

        return (cooldown_state, interval_state), [self.event_provider.elapsed(time)] + [
            self.event_provider.dealt(tick_damage, tick_hit) for _ in range(lapse_count)
        ]

    def use_tick_emitting_trait(
        self,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        dynamics: Dynamics,
        duration_multiplier=1.0,
        hit_multiplier=1,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        if not cooldown_state.available:
            return (
                cooldown_state,
                interval_state,
                dynamics,
            ), [self.event_provider.rejected()]

        damage, hit = self._get_simple_damage_hit()
        delay = self._get_delay()

        cooldown_state.set_time_left(
            dynamics.stat.calculate_cooldown(self._get_cooldown())
        )
        interval_state.set_time_left(self._get_duration() * duration_multiplier)

        return (cooldown_state, interval_state, dynamics), [
            self.event_provider.dealt(damage, hit * hit_multiplier),
            self.event_provider.delayed(delay),
        ]


class StartIntervalWithoutDamageTrait(
    CooldownTrait,
    DurationTrait,
    EventProviderTrait,
    DelayTrait,
):
    def use_tick_emitting_without_damage_trait(
        self,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        if not cooldown_state.available:
            return (
                cooldown_state,
                interval_state,
                dynamics,
            ), self.event_provider.rejected()

        delay = self._get_delay()

        cooldown_state.set_time_left(
            dynamics.stat.calculate_cooldown(self._get_cooldown())
        )
        interval_state.set_time_left(self._get_duration())

        return (cooldown_state, interval_state, dynamics), [
            self.event_provider.delayed(delay),
        ]
