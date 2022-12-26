from simaple.simulate.base import Event
from simaple.simulate.component.state_protocol import (
    CooldownDurationDynamicsGeneric,
    CooldownDynamicsGeneric,
    CooldownDynamicsPeriodicGeneric,
    CooldownGeneric,
    CooldownPeriodicGeneric,
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
            time_left=max(0, state.cooldown.time_left),
            valid=state.cooldown.available,
            cooldown_duration=self._get_cooldown_duration(),
        )


class InvalidatableCooldownTrait(CooldownTrait, InvalidatableTrait, NamedTrait):
    def validity_in_invalidatable_cooldown_trait(
        self, state: CooldownProtocol
    ) -> Validity:
        return self.invalidate_if_disabled(
            Validity(
                name=self._get_name(),
                time_left=max(0, state.cooldown.time_left),
                valid=state.cooldown.available,
                cooldown_duration=self._get_cooldown_duration(),
            )
        )


class UseSimpleAttackTrait(
    CooldownTrait, SimpleDamageTrait, EventProviderTrait, DelayTrait
):
    def use_simple_attack(
        self, state: CooldownDynamicsGeneric
    ) -> tuple[CooldownDynamicsGeneric, list[Event]]:
        state = state.copy()

        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )

        damage, hit = self._get_simple_damage_hit()
        delay = self._get_delay()

        return state, [
            self.event_provider.dealt(damage, hit),
            self.event_provider.delayed(delay),
        ]

    def elapse_simple_attack(
        self, time: float, state: CooldownGeneric
    ) -> tuple[CooldownGeneric, list[Event]]:
        state = state.copy()
        state.cooldown.elapse(time)
        return state, [self.event_provider.elapsed(time)]

    def use_multiple_damage(
        self, state: CooldownDynamicsGeneric, multiple: int
    ) -> tuple[CooldownDynamicsGeneric, list[Event]]:
        state = state.copy()

        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
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
        state: CooldownDurationDynamicsGeneric,
    ) -> tuple[CooldownDurationDynamicsGeneric, list[Event]]:
        state = state.copy()

        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )

        state.lasting.set_time_left(
            state.dynamics.stat.calculate_buff_duration(
                self._get_lasting_duration(state)
            )
        )

        return state, [self.event_provider.delayed(self._get_delay())]

    def elapse_durable_trait(
        self,
        time: float,
        state: CooldownDurationDynamicsGeneric,
    ) -> tuple[CooldownDurationDynamicsGeneric, list[Event]]:
        state = state.copy()

        state.cooldown.elapse(time)
        state.lasting.elapse(time)

        return state, [
            self.event_provider.elapsed(time),
        ]

    def running_in_durable_trait(self, state: DurationProtocol) -> Running:
        return Running(
            name=self._get_name(),
            time_left=state.lasting.time_left,
            lasting_duration=self._get_lasting_duration(state),
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
        state: CooldownPeriodicGeneric,
    ) -> tuple[CooldownPeriodicGeneric, list[Event]]:
        state = state.copy()

        state.cooldown.elapse(time)
        lapse_count = state.periodic.elapse(time)

        tick_damage, tick_hit = self._get_tick_damage_hit(state)

        return state, [self.event_provider.elapsed(time)] + [
            self.event_provider.dealt(tick_damage, tick_hit) for _ in range(lapse_count)
        ]

    def use_tick_emitting_trait(
        self,
        state: CooldownDynamicsPeriodicGeneric,
    ) -> tuple[CooldownDynamicsPeriodicGeneric, list[Event]]:
        state = state.copy()

        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        damage, hit = self._get_simple_damage_hit()
        delay = self._get_delay()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )
        state.periodic.set_time_left(self._get_lasting_duration(state))

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
        state: CooldownDynamicsPeriodicGeneric,
    ) -> tuple[CooldownDynamicsPeriodicGeneric, list[Event]]:
        state = state.copy()

        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        delay = self._get_delay()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )
        state.periodic.set_time_left(self._get_lasting_duration(state))

        return state, [
            self.event_provider.delayed(delay),
        ]
