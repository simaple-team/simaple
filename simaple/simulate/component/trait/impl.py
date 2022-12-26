from simaple.simulate.component.state_protocol import (
    CooldownDurationDynamicsProtocol,
    CooldownDynamicsIntervalProtocol,
    CooldownDynamicsProtocol,
    CooldownIntervalProtocol,
    CooldownProtocol,
    DurationProtocol,
)
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
from simaple.simulate.component.view import Running, Validity


class CooldownValidityTrait(CooldownTrait, NamedTrait):
    def validity_in_cooldown_trait(self, state: CooldownProtocol) -> Validity:
        return Validity(
            name=self._get_name(),
            time_left=max(0, state.cooldown_state.time_left),
            valid=state.cooldown_state.available,
            cooldown=self._get_cooldown(),
        )


class InvalidatableCooldownTrait(CooldownTrait, InvalidatableTrait, NamedTrait):
    def validity_in_invalidatable_cooldown_trait(
        self, state: CooldownProtocol
    ) -> Validity:
        return self.invalidate_if_disabled(
            Validity(
                name=self._get_name(),
                time_left=max(0, state.cooldown_state.time_left),
                valid=state.cooldown_state.available,
                cooldown=self._get_cooldown(),
            )
        )


class UseSimpleAttackTrait(
    CooldownTrait, SimpleDamageTrait, EventProviderTrait, DelayTrait
):
    def use_simple_attack(self, state: CooldownDynamicsProtocol):
        state = state.copy()

        if not state.cooldown_state.available:
            return state, self.event_provider.rejected()

        state.cooldown_state.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown())
        )

        damage, hit = self._get_simple_damage_hit()
        delay = self._get_delay()

        return state, [
            self.event_provider.dealt(damage, hit),
            self.event_provider.delayed(delay),
        ]

    def elapse_simple_attack(self, time: float, state: CooldownProtocol):
        state = state.copy()
        state.cooldown_state.elapse(time)
        return state, self.event_provider.elapsed(time)

    def use_multiple_damage(self, state: CooldownDynamicsProtocol, multiple: int):
        state = state.copy()

        if not state.cooldown_state.available:
            return state, self.event_provider.rejected()

        state.cooldown_state.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown())
        )

        damage, hit = self._get_simple_damage_hit()
        delay = self._get_delay()

        return state, [
            self.event_provider.dealt(damage, hit) for _ in range(multiple)
        ] + [self.event_provider.delayed(delay)]


class DurableTrait(
    CooldownTrait, DurationTrait, EventProviderTrait, DelayTrait, NamedTrait
):
    def use_durable_trait(
        self,
        state: CooldownDurationDynamicsProtocol,
    ):
        state = state.copy()

        if not state.cooldown_state.available:
            return state, self.event_provider.rejected()

        state.cooldown_state.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown())
        )

        state.duration_state.set_time_left(
            state.dynamics.stat.calculate_buff_duration(self._get_duration(state))
        )

        return state, self.event_provider.delayed(self._get_delay())

    def elapse_durable_trait(
        self,
        time: float,
        state: CooldownDurationDynamicsProtocol,
    ):
        state = state.copy()

        state.cooldown_state.elapse(time)
        state.duration_state.elapse(time)

        return state, [
            self.event_provider.elapsed(time),
        ]

    def running_in_durable_trait(self, state: DurationProtocol):
        return Running(
            name=self._get_name(),
            time_left=state.duration_state.time_left,
            duration=self._get_duration(state),
        )


class TickEmittingTrait(
    CooldownTrait,
    TickDamageTrait,
    SimpleDamageTrait,
    DurationTrait,
    EventProviderTrait,
    DelayTrait,
):
    def elapse_tick_emitting_trait(
        self,
        time: float,
        state: CooldownIntervalProtocol,
        hit_multiplier=1,
    ):
        state = state.copy()

        state.cooldown_state.elapse(time)
        lapse_count = state.interval_state.elapse(time)

        tick_damage, tick_hit = self._get_tick_damage_hit()

        return state, [self.event_provider.elapsed(time)] + [
            self.event_provider.dealt(tick_damage, tick_hit * hit_multiplier)
            for _ in range(lapse_count)
        ]

    def use_tick_emitting_trait(
        self,
        state: CooldownDynamicsIntervalProtocol,
        duration_multiplier=1.0,
    ):
        state = state.copy()

        if not state.cooldown_state.available:
            return state, [self.event_provider.rejected()]

        damage, hit = self._get_simple_damage_hit()
        delay = self._get_delay()

        state.cooldown_state.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown())
        )
        state.interval_state.set_time_left(
            self._get_duration(state) * duration_multiplier
        )

        return state, [
            self.event_provider.dealt(damage, hit),
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
        state: CooldownDynamicsIntervalProtocol,
    ):
        state = state.copy()

        if not state.cooldown_state.available:
            return state, self.event_provider.rejected()

        delay = self._get_delay()

        state.cooldown_state.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown())
        )
        state.interval_state.set_time_left(self._get_duration(state))

        return state, [
            self.event_provider.delayed(delay),
        ]
