from simaple.core import Stat
from simaple.simulate.base import State
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.skill import (
    CooldownState,
    IntervalState,
    SkillComponent,
)
from simaple.simulate.component.state import DurationState, StackState
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    InvalidatableCooldownTrait,
    TickEmittingTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.util import is_rejected
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.global_property import Dynamics


class EtherState(StackState):
    creation_step: int
    order_consume: int

    def get_creation_count(self) -> int:
        return min(self.stack // self.creation_step, 3) * 2

    def is_order_valid(self) -> bool:
        return self.stack >= self.order_consume


class RestoreDurationState(DurationState):
    ether_multiplier: float

    def get_gain_rate(self) -> float:
        if self.enabled():
            return 1 + self.ether_multiplier / 100
        return 1


class AdeleEtherComponent(Component):
    maximum_stack: int
    tick_interval: float
    stack_per_tick: int
    stack_per_trigger: int
    stack_per_resonance: int
    creation_step: int
    order_consume: int

    listening_actions: dict[str, str] = {
        "디바이드.use.emitted.global.delay": "trigger",
        "레조넌스.use.emitted.global.delay": "resonance",
        "오더.use.emitted.global.delay": "order",
    }
    binds: dict[str, str] = {"restore_state": ".리스토어(버프).duration_state"}

    def get_default_state(self):
        return {
            "ether_state": EtherState(
                maximum_stack=self.maximum_stack,
                creation_step=self.creation_step,
                order_consume=self.order_consume,
            ),
            "interval_state": IntervalState(
                interval=self.tick_interval, interval_time_left=999_999_999
            ),
        }

    @reducer_method
    def elapse(
        self, time: float, ether_state: EtherState, interval_state: IntervalState
    ):
        ether_state = ether_state.copy()
        interval_state = interval_state.copy()

        lapse_count = interval_state.elapse(time)
        ether_state.increase(lapse_count * self.stack_per_tick)

        return (ether_state, interval_state), [self.event_provider.elapsed(time)]

    @reducer_method
    def trigger(
        self, _: None, ether_state: EtherState, restore_state: RestoreDurationState
    ):
        ether_state = ether_state.copy()

        ether_state.increase(
            int(self.stack_per_trigger * restore_state.get_gain_rate())
        )

        return (ether_state, restore_state), []

    @reducer_method
    def resonance(self, _: None, ether_state: EtherState):
        ether_state = ether_state.copy()

        ether_state.increase(self.stack_per_resonance)

        return (ether_state), []

    @reducer_method
    def order(self, _: None, ether_state: EtherState):
        ether_state = ether_state.copy()

        ether_state.decrease(self.order_consume)

        return (ether_state), []

    @view_method
    def running(self, ether_state: EtherState):
        return Running(
            name=self.name,
            time_left=999_999_999,
            duration=999_999_999,
            stack=ether_state.get_stack(),
        )


class AdeleCreationComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait
):
    name: str
    damage: float
    hit_per_sword: float
    cooldown: float
    delay: float

    listening_actions: dict[str, str] = {"디바이드.use": "trigger"}
    binds: dict[str, str] = {"ether_state": ".에테르.ether_state"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, cooldown_state: CooldownState):
        return self.elapse_simple_attack(time, cooldown_state)

    @reducer_method
    def trigger(
        self,
        _: None,
        cooldown_state: CooldownState,
        ether_state: EtherState,
        dynamics: Dynamics,
    ):
        (cooldown_state, dynamics), event = self.use_multiple_damage(
            cooldown_state, dynamics, ether_state.get_creation_count()
        )

        return (cooldown_state, ether_state, dynamics), event

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_invalidatable_cooldown_trait(cooldown_state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit_per_sword


class OrderState(State):
    running_swords: list[tuple[float, float]] = []  # (counter, time_left)[]
    interval: float

    def get_time_left(self) -> float:
        if len(self.running_swords) <= 0:
            return 0

        _, time_left = self.running_swords[-1]
        return time_left

    def enabled(self):
        return len(self.running_swords) > 0

    def add_running(
        self, initial_counter: float, time_left: float, max_sword_count: int
    ):
        result = self.running_swords + [(initial_counter, time_left)]
        self._set_running_swords(result, max_sword_count)

    def resolving(self, time: float, max_sword_count: int):
        result: list[tuple[float, float]] = []
        for index, _ in enumerate(self.running_swords):
            counter, time_left = self.running_swords[index]
            maximum_elapsed = max(0, int(time_left // self.interval))

            time_left -= time
            counter -= time
            elapse_count = 0

            while counter <= 0 and elapse_count < maximum_elapsed:
                counter += self.interval
                elapse_count += 1
                yield 1

            if time_left > 0:
                result.append((counter, time_left))

        self._set_running_swords(result, max_sword_count)

    def _set_running_swords(
        self, swords: list[tuple[float, float]], max_sword_count: int
    ):
        self.running_swords = swords
        while self.get_sword_count() > max_sword_count:
            self.running_swords = self.running_swords[1:]

    def get_sword_count(self) -> int:
        return len(self.running_swords) * 2


class AdeleOrderComponent(SkillComponent, CooldownValidityTrait):
    tick_interval: float
    tick_damage: float
    tick_hit: float
    duration: float
    maximum_stack: int
    restore_maximum_stack: int

    binds: dict[str, str] = {
        "ether_state": ".에테르.ether_state",
        "restore_state": ".리스토어(버프).duration_state",
    }

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "order_state": OrderState(interval=self.tick_interval),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        order_state: OrderState,
        restore_state: RestoreDurationState,
    ):
        cooldown_state = cooldown_state.copy()
        order_state = order_state.copy()

        cooldown_state.elapse(time)

        dealing_events = []

        for _ in order_state.resolving(time, self._max_sword_count(restore_state)):
            dealing_events.append(
                self.event_provider.dealt(self.tick_damage, self.tick_hit)
            )

        return (cooldown_state, order_state, restore_state), [
            self.event_provider.elapsed(time)
        ] + dealing_events

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        dynamics: Dynamics,
        order_state: OrderState,
        ether_state: EtherState,
        restore_state: RestoreDurationState,
    ):
        order_state = order_state.copy()
        cooldown_state = cooldown_state.copy()

        if not ether_state.is_order_valid():
            return (
                cooldown_state,
                dynamics,
                order_state,
                ether_state,
            ), [self.event_provider.rejected()]

        if not cooldown_state.available:
            return (
                cooldown_state,
                dynamics,
                order_state,
                ether_state,
            ), [self.event_provider.rejected()]

        damage, hit = self.tick_damage, self.tick_hit
        delay = self._get_delay()

        cooldown_state.set_time_left(
            dynamics.stat.calculate_cooldown(self._get_cooldown())
        )

        order_state.add_running(0, self.duration, self._max_sword_count(restore_state))

        return (cooldown_state, dynamics, order_state, ether_state, restore_state), [
            self.event_provider.dealt(damage, hit),
            self.event_provider.delayed(delay),
        ]

    @view_method
    def validity(self, cooldown_state: CooldownState, ether_state: EtherState):
        return Validity(
            name=self._get_name(),
            time_left=max(0, cooldown_state.time_left),
            valid=cooldown_state.available and ether_state.is_order_valid(),
            cooldown=self._get_cooldown(),
        )

    @view_method
    def running(self, order_state: OrderState) -> Running:
        return Running(
            name=self.name,
            time_left=order_state.get_time_left(),
            duration=self.duration,
            stack=order_state.get_sword_count(),
        )

    def _max_sword_count(self, restore_state: RestoreDurationState):
        if restore_state.enabled():
            return self.restore_maximum_stack

        return self.maximum_stack


class AdeleGatheringComponent(SkillComponent, UseSimpleAttackTrait):
    damage: float
    hit_per_sword: float

    binds: dict[str, str] = {"order_state": ".오더.order_state"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        dynamics: Dynamics,
        order_state: OrderState,
    ):
        (states, event) = self.use_multiple_damage(
            cooldown_state, dynamics, order_state.get_sword_count()
        )

        return (*states, order_state), event

    @reducer_method
    def elapse(self, time: float, cooldown_state: CooldownState):
        return self.elapse_simple_attack(time, cooldown_state)

    @view_method
    def validity(self, cooldown_state: CooldownState, order_state: OrderState):
        return Validity(
            name=self.name,
            time_left=max(0, cooldown_state.time_left),
            valid=cooldown_state.available and order_state.get_sword_count() > 0,
            cooldown=self._get_cooldown(),
        )

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit_per_sword


class AdeleBlossomComponent(SkillComponent, UseSimpleAttackTrait):
    damage: float
    hit_per_sword: float
    exceeded_stat: Stat

    binds: dict[str, str] = {"order_state": ".오더.order_state"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        order_state: OrderState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()
        sword_count = order_state.get_sword_count()

        if not cooldown_state.available:
            return (
                cooldown_state,
                order_state,
                dynamics,
            ), self.event_provider.rejected()

        if sword_count <= 0:
            return (
                cooldown_state,
                order_state,
                dynamics,
            ), self.event_provider.rejected()

        cooldown_state.set_time_left(
            dynamics.stat.calculate_cooldown(self._get_cooldown())
        )

        damage, hit = self._get_simple_damage_hit()
        delay = self._get_delay()

        return (cooldown_state, order_state, dynamics), [
            self.event_provider.dealt(damage, hit)
        ] + [
            self.event_provider.dealt(
                damage,
                hit,
                modifier=self.exceeded_stat,
            )
            for _ in range(order_state.get_sword_count() - 1)
        ] + [
            self.event_provider.delayed(delay)
        ]

    @reducer_method
    def elapse(self, time: float, cooldown_state: CooldownState):
        return self.elapse_simple_attack(time, cooldown_state)

    @view_method
    def validity(self, cooldown_state: CooldownState, order_state: OrderState):
        return Validity(
            name=self.name,
            time_left=max(0, cooldown_state.time_left),
            valid=cooldown_state.available and order_state.get_sword_count() > 0,
            cooldown=self._get_cooldown(),
        )

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit_per_sword


class AdeleRuinComponent(
    SkillComponent,
    CooldownValidityTrait,
):
    tick_interval_first: float
    tick_damage_first: float
    tick_hit_first: float
    duration_first: float

    tick_interval_second: float
    tick_damage_second: float
    tick_hit_second: float
    duration_second: float

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "interval_state_first": IntervalState(interval=self.tick_interval_first),
            "interval_state_second": IntervalState(interval=self.tick_interval_second),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        interval_state_first: IntervalState,
        interval_state_second: IntervalState,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state_first = interval_state_first.copy()
        interval_state_second = interval_state_second.copy()

        cooldown_state.elapse(time)
        lapse_count_first = interval_state_first.elapse(time)
        lapse_count_second = interval_state_second.elapse(time)

        return (cooldown_state, interval_state_first, interval_state_second), [
            self.event_provider.elapsed(time)
        ] + [
            self.event_provider.dealt(self.tick_damage_first, self.tick_hit_first)
            for _ in range(lapse_count_first)
        ] + [
            self.event_provider.dealt(self.tick_damage_second, self.tick_hit_second)
            for _ in range(lapse_count_second)
        ]

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        interval_state_first: IntervalState,
        interval_state_second: IntervalState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state_first = interval_state_first.copy()
        interval_state_second = interval_state_second.copy()

        if not cooldown_state.available:
            return (
                cooldown_state,
                interval_state_first,
                interval_state_second,
                dynamics,
            ), [self.event_provider.rejected()]

        delay = self._get_delay()

        cooldown_state.set_time_left(
            dynamics.stat.calculate_cooldown(self._get_cooldown())
        )
        interval_state_first.set_time_left(self.duration_first)
        interval_state_second.set_time_left(
            self.duration_first + self.duration_second, self.duration_first
        )

        return (
            cooldown_state,
            interval_state_first,
            interval_state_second,
            dynamics,
        ), [
            self.event_provider.delayed(delay),
        ]

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_cooldown_trait(cooldown_state)

    @view_method
    def running(
        self,
        interval_state_second: IntervalState,
    ) -> Running:
        return Running(
            name=self.name,
            time_left=interval_state_second.interval_time_left,
            duration=self.duration_first + self.duration_second,
        )


class AdeleRestoreBuffComponent(SkillComponent):
    duration: float
    ether_multiplier: float
    stat: Stat

    def get_default_state(self):
        return {
            "duration_state": RestoreDurationState(
                time_left=0, ether_multiplier=self.ether_multiplier
            )
        }

    @reducer_method
    def use(self, _: None, duration_state: RestoreDurationState, dynamics: Dynamics):
        duration_state = duration_state.copy()
        duration_state.set_time_left(
            dynamics.stat.calculate_buff_duration(self.duration)
        )
        return (duration_state, dynamics), [self.event_provider.delayed(self.delay)]

    @reducer_method
    def elapse(self, time: float, duration_state: DurationState):
        duration_state = duration_state.copy()
        duration_state.elapse(time)
        return (duration_state), [
            self.event_provider.elapsed(time),
        ]

    @view_method
    def buff(self, duration_state: RestoreDurationState):
        if duration_state.enabled():
            return self.stat

        return None

    @view_method
    def running(self, duration_state: RestoreDurationState) -> Running:
        return Running(
            name=self.name,
            time_left=duration_state.time_left,
            duration=self.duration,
        )


class AdeleStormComponent(SkillComponent, TickEmittingTrait, CooldownValidityTrait):
    tick_interval: float
    tick_damage: float
    tick_hit: float
    duration: float
    maximum_stack: int

    binds: dict[str, str] = {"order_state": ".오더.order_state"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
            "stack_state": StackState(maximum_stack=self.maximum_stack),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        stack_state: StackState,
    ):
        (cooldown_state, interval_state), event = self.elapse_tick_emitting_trait(
            time,
            cooldown_state,
            interval_state,
            hit_multiplier=stack_state.stack,
        )

        return (cooldown_state, interval_state, stack_state), event

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        dynamics: Dynamics,
        stack_state: StackState,
        order_state: OrderState,
    ):
        sword_count = order_state.get_sword_count()

        if sword_count <= 0:
            return (cooldown_state, interval_state, dynamics, order_state), [
                self.event_provider.rejected()
            ]

        states, events = self.use_tick_emitting_trait(
            cooldown_state, interval_state, dynamics
        )
        if not is_rejected(events):
            stack_state.reset(sword_count)

        return (*states, stack_state, order_state), events

    @view_method
    def validity(self, cooldown_state: CooldownState, order_state: OrderState):
        return Validity(
            name=self._get_name(),
            time_left=max(0, cooldown_state.time_left),
            valid=cooldown_state.available and order_state.get_sword_count() > 0,
            cooldown=self._get_cooldown(),
        )

    @view_method
    def running(
        self, interval_state: IntervalState, stack_state: StackState
    ) -> Running:
        return Running(
            name=self.name,
            time_left=interval_state.interval_time_left,
            duration=self._get_duration(),
            stack=stack_state.stack,
        )

    def _get_duration(self) -> float:
        return self.duration

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        # TODO: TickEmittingTrait should not extend SimpleDamageTrait. Remove this method
        return 0, 0

    def _get_tick_damage_hit(self) -> tuple[float, float]:
        return self.tick_damage, self.tick_hit
