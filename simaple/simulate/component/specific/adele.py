from simaple.core import Stat
from simaple.simulate.base import Entity
from simaple.simulate.component.base import (
    Component,
    ReducerState,
    reducer_method,
    view_method,
)
from simaple.simulate.component.entity import Lasting, Stack
from simaple.simulate.component.skill import Cooldown, Periodic, SkillComponent
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    InvalidatableCooldownTrait,
    PeriodicWithSimpleDamageTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.util import is_rejected
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.global_property import Dynamics


class EtherGauge(Stack):
    creation_step: int
    order_consume: int

    def get_creation_count(self) -> int:
        return min(self.stack // self.creation_step, 3) * 2

    def is_order_valid(self) -> bool:
        return self.stack >= self.order_consume

    def decrease_order(self):
        self.decrease(self.order_consume)


class RestoreLasting(Lasting):
    ether_multiplier: float

    def get_gain_rate(self) -> float:
        if self.enabled():
            return 1 + self.ether_multiplier / 100
        return 1


class EtherState(ReducerState):
    ether_gauge: EtherGauge
    periodic: Periodic
    restore_lasting: RestoreLasting


class AdeleEtherComponent(Component):
    maximum_stack: int
    periodic_interval: float
    stack_per_period: int
    stack_per_trigger: int
    stack_per_resonance: int
    creation_step: int
    order_consume: int

    binds: dict[str, str] = {"restore_lasting": ".리스토어(버프).lasting"}

    def get_default_state(self):
        return {
            "ether_gauge": EtherGauge(
                maximum_stack=self.maximum_stack,
                creation_step=self.creation_step,
                order_consume=self.order_consume,
            ),
            "periodic": Periodic(
                interval=self.periodic_interval, time_left=999_999_999
            ),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: EtherState,
    ):
        state = state.deepcopy()

        lapse_count = state.periodic.elapse(time)
        state.ether_gauge.increase(lapse_count * self.stack_per_period)

        return state, [self.event_provider.elapsed(time)]

    @reducer_method
    def trigger(
        self,
        _: None,
        state: EtherState,
    ):
        state = state.deepcopy()

        state.ether_gauge.increase(
            int(self.stack_per_trigger * state.restore_lasting.get_gain_rate())
        )

        return state, []

    @reducer_method
    def resonance(
        self,
        _: None,
        state: EtherState,
    ):
        state = state.deepcopy()

        state.ether_gauge.increase(self.stack_per_resonance)

        return state, []

    @reducer_method
    def order(
        self,
        _: None,
        state: EtherState,
    ):
        state = state.deepcopy()

        state.ether_gauge.decrease_order()

        return (state), []

    @view_method
    def running(
        self,
        state: EtherState,
    ):
        return Running(
            name=self.name,
            time_left=999_999_999,
            lasting_duration=999_999_999,
            stack=state.ether_gauge.get_stack(),
        )


class CreationState(ReducerState):
    ether_gauge: EtherGauge
    cooldown: Cooldown
    dynamics: Dynamics


class AdeleCreationComponent(
    SkillComponent, InvalidatableCooldownTrait, UseSimpleAttackTrait
):
    name: str
    damage: float
    hit_per_sword: float
    cooldown_duration: float
    delay: float

    binds: dict[str, str] = {"ether_gauge": ".에테르.ether_gauge"}

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: CreationState):
        return self.elapse_simple_attack(time, state)

    @reducer_method
    def trigger(self, _: None, state: CreationState):
        return self.use_multiple_damage(state, state.ether_gauge.get_creation_count())

    @view_method
    def validity(self, state: CreationState):
        return self.validity_in_invalidatable_cooldown_trait(state)

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit_per_sword


class OrderSword(Entity):
    running_swords: list[tuple[float, float]] = []  # (counter, time_left)[]
    interval: float

    def get_time_left(self) -> float:
        if len(self.running_swords) == 0:
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


class AdeleOrderState(ReducerState):
    ether_gauge: EtherGauge
    restore_lasting: RestoreLasting
    cooldown: Cooldown
    order_sword: OrderSword
    dynamics: Dynamics


# TODO: 게더링-블로섬 도중 타격 미발생 및 지속시간 정지
class AdeleOrderComponent(SkillComponent):
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float
    maximum_stack: int
    restore_maximum_stack: int

    binds: dict[str, str] = {
        "ether_gauge": ".에테르.ether_gauge",
        "restore_lasting": ".리스토어(버프).lasting",
    }

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "order_sword": OrderSword(interval=self.periodic_interval),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: AdeleOrderState,
    ):
        state = state.deepcopy()

        state.cooldown.elapse(time)

        dealing_events = []

        for _ in state.order_sword.resolving(time, self._max_sword_count(state)):
            dealing_events.append(
                self.event_provider.dealt(self.periodic_damage, self.periodic_hit)
            )

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(
        self,
        _: None,
        state: AdeleOrderState,
    ):
        state = state.deepcopy()

        if not (state.ether_gauge.is_order_valid() and state.cooldown.available):
            return state, [self.event_provider.rejected()]

        damage, hit = self.periodic_damage, self.periodic_hit
        delay = self._get_delay()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )

        state.order_sword.add_running(
            0, self.lasting_duration, self._max_sword_count(state)
        )

        return state, [
            self.event_provider.dealt(damage, hit),
            self.event_provider.delayed(delay),
        ]

    @view_method
    def validity(self, state: AdeleOrderState):
        return Validity(
            name=self._get_name(),
            time_left=max(0, state.cooldown.time_left),
            valid=state.cooldown.available and state.ether_gauge.is_order_valid(),
            cooldown_duration=self._get_cooldown_duration(),
        )

    @view_method
    def running(self, state: AdeleOrderState) -> Running:
        return Running(
            name=self.name,
            time_left=state.order_sword.get_time_left(),
            lasting_duration=self.lasting_duration,
            stack=state.order_sword.get_sword_count(),
        )

    def _max_sword_count(self, state: AdeleOrderState):
        if state.restore_lasting.enabled():
            return self.restore_maximum_stack

        return self.maximum_stack


class AdeleOrderUsingState(ReducerState):
    order_sword: OrderSword
    cooldown: Cooldown
    dynamics: Dynamics


class AdeleGatheringComponent(SkillComponent, UseSimpleAttackTrait):
    damage: float
    hit_per_sword: float

    binds: dict[str, str] = {"order_sword": ".오더.order_sword"}

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: AdeleOrderUsingState,
    ):
        return self.use_multiple_damage(state, state.order_sword.get_sword_count())

    @reducer_method
    def elapse(self, time: float, state: AdeleOrderUsingState):
        return self.elapse_simple_attack(time, state)

    @view_method
    def validity(self, state: AdeleOrderUsingState):
        return Validity(
            name=self.name,
            time_left=max(0, state.cooldown.time_left),
            valid=state.cooldown.available and state.order_sword.get_sword_count() > 0,
            cooldown_duration=self._get_cooldown_duration(),
        )

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit_per_sword


class AdeleBlossomComponent(SkillComponent, UseSimpleAttackTrait):
    damage: float
    hit_per_sword: float
    exceeded_stat: Stat

    binds: dict[str, str] = {"order_sword": ".오더.order_sword"}

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: AdeleOrderUsingState,
    ):
        state = state.deepcopy()

        if not self._is_valid(state):
            return state, [self.event_provider.rejected()]

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )

        damage, hit = self._get_simple_damage_hit()
        delay = self._get_delay()

        return (
            state,
            [self.event_provider.dealt(damage, hit)]
            + [
                self.event_provider.dealt(
                    damage,
                    hit,
                    modifier=self.exceeded_stat,
                )
                for _ in range(state.order_sword.get_sword_count() - 1)
            ]
            + [self.event_provider.delayed(delay)],
        )

    @reducer_method
    def elapse(
        self,
        time: float,
        state: AdeleOrderUsingState,
    ):
        return self.elapse_simple_attack(time, state)

    @view_method
    def validity(
        self,
        state: AdeleOrderUsingState,
    ):
        return Validity(
            name=self.name,
            time_left=max(0, state.cooldown.time_left),
            valid=state.cooldown.available and state.order_sword.get_sword_count() > 0,
            cooldown_duration=self._is_valid(state),
        )

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit_per_sword

    def _is_valid(self, state: AdeleOrderUsingState):
        return state.cooldown.available and state.order_sword.get_sword_count() > 0


class AdeleRuinState(ReducerState):
    cooldown: Cooldown
    interval_state_first: Periodic
    interval_state_second: Periodic
    dynamics: Dynamics


class AdeleRuinComponent(
    SkillComponent,
    CooldownValidityTrait,
):
    periodic_interval_first: float
    periodic_damage_first: float
    periodic_hit_first: float
    lasting_duration_first: float

    periodic_interval_second: float
    periodic_damage_second: float
    periodic_hit_second: float
    lasting_duration_second: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "interval_state_first": Periodic(interval=self.periodic_interval_first),
            "interval_state_second": Periodic(interval=self.periodic_interval_second),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: AdeleRuinState,
    ):
        state = state.deepcopy()

        state.cooldown.elapse(time)
        lapse_count_first = state.interval_state_first.elapse(time)
        lapse_count_second = state.interval_state_second.elapse(time)

        return state, [self.event_provider.elapsed(time)] + [
            self.event_provider.dealt(
                self.periodic_damage_first, self.periodic_hit_first
            )
            for _ in range(lapse_count_first)
        ] + [
            self.event_provider.dealt(
                self.periodic_damage_second, self.periodic_hit_second
            )
            for _ in range(lapse_count_second)
        ]

    @reducer_method
    def use(
        self,
        _: None,
        state: AdeleRuinState,
    ):
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, [self.event_provider.rejected()]

        delay = self._get_delay()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )
        state.interval_state_first.set_time_left(time=self.lasting_duration_first)
        state.interval_state_second.set_time_left(
            time=self.lasting_duration_first + self.lasting_duration_second,
            initial_counter=self.lasting_duration_first,
        )

        return state, [
            self.event_provider.delayed(delay),
        ]

    @view_method
    def validity(
        self,
        state: AdeleRuinState,
    ):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(
        self,
        state: AdeleRuinState,
    ) -> Running:
        return Running(
            name=self.name,
            time_left=state.interval_state_second.time_left,
            lasting_duration=self.lasting_duration_first + self.lasting_duration_second,
        )


class AdeleRestoreState(ReducerState):
    lasting: RestoreLasting
    dynamics: Dynamics


class AdeleRestoreBuffComponent(SkillComponent):
    lasting_duration: float
    ether_multiplier: float
    stat: Stat

    def get_default_state(self):
        return {
            "lasting": RestoreLasting(
                time_left=0, ether_multiplier=self.ether_multiplier
            )
        }

    @reducer_method
    def use(self, _: None, state: AdeleRestoreState):
        state = state.deepcopy()
        state.lasting.set_time_left(
            state.dynamics.stat.calculate_buff_duration(self.lasting_duration)
        )
        return state, [self.event_provider.delayed(self.delay)]

    @reducer_method
    def elapse(self, time: float, state: AdeleRestoreState):
        state = state.deepcopy()
        state.lasting.elapse(time)
        return state, [self.event_provider.elapsed(time)]

    @view_method
    def buff(self, state: AdeleRestoreState):
        if state.lasting.enabled():
            return self.stat

        return None

    @view_method
    def running(self, state: AdeleRestoreState) -> Running:
        return Running(
            name=self.name,
            time_left=state.lasting.time_left,
            lasting_duration=self.lasting_duration,
        )


class AdeleStormState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    stack: Stack
    dynamics: Dynamics
    order_sword: OrderSword


class AdeleStormComponent(
    SkillComponent, PeriodicWithSimpleDamageTrait, CooldownValidityTrait
):
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float
    maximum_stack: int

    binds: dict[str, str] = {"order_sword": ".오더.order_sword"}

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
            "stack": Stack(maximum_stack=self.maximum_stack),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: AdeleStormState,
    ):
        return self.elapse_periodic_damage_trait(time, state)

    @reducer_method
    def use(self, _: None, state: AdeleStormState):
        sword_count = state.order_sword.get_sword_count()

        if sword_count <= 0:
            return state, [self.event_provider.rejected()]

        state, events = self.use_periodic_damage_trait(state)
        if not is_rejected(events):
            state.stack.reset(sword_count)

        return state, events

    @view_method
    def validity(self, state: AdeleStormState):
        return Validity(
            name=self._get_name(),
            time_left=max(0, state.cooldown.time_left),
            valid=state.cooldown.available and state.order_sword.get_sword_count() > 0,
            cooldown_duration=self._get_cooldown_duration(),
        )

    @view_method
    def running(self, state: AdeleStormState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
            stack=state.stack.stack,
        )

    def _get_lasting_duration(self, state: AdeleStormState) -> float:
        return self.lasting_duration

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        # TODO: TickEmittingTrait should not extend SimpleDamageTrait. Remove this method
        return 0, 0

    def _get_periodic_damage_hit(self, state: AdeleStormState) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit * state.stack.stack
