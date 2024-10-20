from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
import simaple.simulate.component.trait.simple_attack as simple_attack
from simaple.core import Stat
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting, Periodic, Stack
from simaple.simulate.component.util import ignore_rejected, is_rejected
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.core.base import Entity
from simaple.simulate.event import EmptyEvent
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


class EtherState(TypedDict):
    ether_gauge: EtherGauge
    periodic: Periodic
    restore_lasting: RestoreLasting


class AdeleEtherComponent(Component):
    id: str
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
                interval=self.periodic_interval,
                time_left=999_999_999,
                initial_counter=self.periodic_interval,
                interval_counter=self.periodic_interval,
            ),
            "restore_lasting": RestoreLasting(time_left=0, ether_multiplier=0),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: EtherState,
    ):
        periodic, ether_gauge = (
            state["periodic"].model_copy(),
            state["ether_gauge"].model_copy(),
        )

        lapse_count = periodic.elapse(time)
        ether_gauge.increase(lapse_count * self.stack_per_period)

        state["periodic"] = periodic
        state["ether_gauge"] = ether_gauge

        return state, [EmptyEvent.elapsed(time)]

    @reducer_method
    def trigger(
        self,
        _: None,
        state: EtherState,
    ):
        ether_gauge = state["ether_gauge"].model_copy()

        ether_gauge.increase(
            int(self.stack_per_trigger * state["restore_lasting"].get_gain_rate())
        )

        state["ether_gauge"] = ether_gauge

        return state, []

    @reducer_method
    def resonance(
        self,
        _: None,
        state: EtherState,
    ):
        ether_gauge = state["ether_gauge"].model_copy()
        ether_gauge.increase(self.stack_per_resonance)
        state["ether_gauge"] = ether_gauge

        return state, []

    @reducer_method
    def order(
        self,
        _: None,
        state: EtherState,
    ):
        ether_gauge = state["ether_gauge"].model_copy()
        ether_gauge.decrease_order()
        state["ether_gauge"] = ether_gauge

        return (state), []

    @view_method
    def running(
        self,
        state: EtherState,
    ):
        return Running(
            id=self.id,
            name=self.name,
            time_left=999_999_999,
            lasting_duration=999_999_999,
            stack=state["ether_gauge"].get_stack(),
        )


class CreationState(TypedDict):
    ether_gauge: EtherGauge
    cooldown: Cooldown
    dynamics: Dynamics


class AdeleCreationComponentProps(TypedDict):
    id: str
    name: str
    damage: float
    hit_per_sword: float
    cooldown_duration: float
    delay: float


class AdeleCreationComponent(
    Component,
):
    name: str
    damage: float
    hit_per_sword: float
    cooldown_duration: float
    delay: float

    binds: dict[str, str] = {"ether_gauge": ".에테르.ether_gauge"}

    def get_default_state(self) -> CreationState:
        return {
            "cooldown": Cooldown(time_left=0),
            "ether_gauge": EtherGauge(
                maximum_stack=6, creation_step=2, order_consume=2
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> AdeleCreationComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit_per_sword": self.hit_per_sword,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
        }

    @reducer_method
    def elapse(self, time: float, state: CreationState):
        return simple_attack.elapse(state, {"time": time})

    @reducer_method
    @ignore_rejected
    def trigger(self, _: None, state: CreationState):
        if not state["cooldown"].available:
            return state, []

        state["cooldown"].set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )

        return state, [
            self.event_provider.dealt(self.damage, self.hit_per_sword)
            for _ in range(state["ether_gauge"].get_creation_count())
        ] + [self.event_provider.delayed(self.delay)]

    @view_method
    def validity(self, state: CreationState):
        return cooldown_trait.validity_view(state, **self.get_props())


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


class AdeleOrderState(TypedDict):
    ether_gauge: EtherGauge
    restore_lasting: RestoreLasting
    cooldown: Cooldown
    order_sword: OrderSword
    dynamics: Dynamics


# TODO: 게더링-블로섬 도중 타격 미발생 및 지속시간 정지
class AdeleOrderComponent(Component):
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float
    maximum_stack: int
    restore_maximum_stack: int
    delay: float
    cooldown_duration: float

    binds: dict[str, str] = {
        "ether_gauge": ".에테르.ether_gauge",
        "restore_lasting": ".리스토어(버프).lasting",
    }

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "order_sword": OrderSword(interval=self.periodic_interval),
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "restore_lasting": RestoreLasting(time_left=0, ether_multiplier=0),
            "ether_gauge": EtherGauge(
                maximum_stack=6, creation_step=2, order_consume=2
            ),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: AdeleOrderState,
    ):
        ether_gauge, cooldown, order_sword = (
            state["ether_gauge"].model_copy(),
            state["cooldown"].model_copy(),
            state["order_sword"].model_copy(),
        )

        cooldown.elapse(time)

        dealing_events = []

        for _ in order_sword.resolving(time, self._max_sword_count(state)):
            dealing_events.append(
                EmptyEvent.dealt(self.periodic_damage, self.periodic_hit)
            )

        state["ether_gauge"] = ether_gauge
        state["cooldown"] = cooldown
        state["order_sword"] = order_sword

        return state, [EmptyEvent.elapsed(time)] + dealing_events

    @reducer_method
    def use(
        self,
        _: None,
        state: AdeleOrderState,
    ):
        ether_gauge, cooldown, order_sword = (
            state["ether_gauge"].model_copy(),
            state["cooldown"].model_copy(),
            state["order_sword"].model_copy(),
        )

        if not (ether_gauge.is_order_valid() and cooldown.available):
            return state, [EmptyEvent.rejected()]

        damage, hit = self.periodic_damage, self.periodic_hit
        delay = self.delay

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )

        order_sword.add_running(0, self.lasting_duration, self._max_sword_count(state))
        state["ether_gauge"] = ether_gauge
        state["cooldown"] = cooldown
        state["order_sword"] = order_sword

        return state, [
            EmptyEvent.dealt(damage, hit),
            EmptyEvent.delayed(delay),
        ]

    @view_method
    def validity(self, state: AdeleOrderState):
        return Validity(
            id=self.id,
            name=self.name,
            time_left=state["cooldown"].minimum_time_to_available(),
            valid=state["cooldown"].available and state["ether_gauge"].is_order_valid(),
            cooldown_duration=self.cooldown_duration,
        )

    @view_method
    def running(self, state: AdeleOrderState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["order_sword"].get_time_left(),
            lasting_duration=self.lasting_duration,
            stack=state["order_sword"].get_sword_count(),
        )

    def _max_sword_count(self, state: AdeleOrderState):
        if state["restore_lasting"].enabled():
            return self.restore_maximum_stack

        return self.maximum_stack


class AdeleOrderUsingState(TypedDict):
    order_sword: OrderSword
    cooldown: Cooldown
    dynamics: Dynamics


class AdeleGatheringComponent(Component):
    damage: float
    hit_per_sword: float
    cooldown_duration: float
    delay: float

    binds: dict[str, str] = {"order_sword": ".오더 VI.order_sword"}

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "order_sword": OrderSword(interval=1),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: AdeleOrderUsingState,
    ):
        cooldown = state["cooldown"].model_copy()

        if not cooldown.available:
            return state, [self.event_provider.rejected()]

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        state["cooldown"] = cooldown

        return state, [
            self.event_provider.dealt(self.damage, self.hit_per_sword)
            for _ in range(state["order_sword"].get_sword_count())
        ] + [self.event_provider.delayed(self.delay)]

    @reducer_method
    def elapse(self, time: float, state: AdeleOrderUsingState):
        return simple_attack.elapse(state, {"time": time})

    @view_method
    def validity(self, state: AdeleOrderUsingState):
        return Validity(
            id=self.id,
            name=self.name,
            time_left=state["cooldown"].minimum_time_to_available(),
            valid=state["cooldown"].available
            and state["order_sword"].get_sword_count() > 0,
            cooldown_duration=self.cooldown_duration,
        )

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit_per_sword


class AdeleBlossomComponent(Component):
    damage: float
    hit_per_sword: float
    exceeded_stat: Stat
    delay: float
    cooldown_duration: float

    binds: dict[str, str] = {"order_sword": ".오더 VI.order_sword"}

    def get_default_state(self) -> AdeleOrderUsingState:
        return {
            "cooldown": Cooldown(time_left=0),
            "order_sword": OrderSword(interval=1),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: AdeleOrderUsingState,
    ):
        cooldown = state["cooldown"].model_copy()

        if not self._is_valid(state):
            return state, [EmptyEvent.rejected()]

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        state["cooldown"] = cooldown

        return (
            state,
            [EmptyEvent.dealt(self.damage, self.hit_per_sword)]
            + [
                EmptyEvent.dealt(
                    self.damage,
                    self.hit_per_sword,
                    modifier=self.exceeded_stat,
                )
                for _ in range(state["order_sword"].get_sword_count() - 1)
            ]
            + [EmptyEvent.delayed(self.delay)],
        )

    @reducer_method
    def elapse(
        self,
        time: float,
        state: AdeleOrderUsingState,
    ):
        return simple_attack.elapse(state, {"time": time})

    @view_method
    def validity(
        self,
        state: AdeleOrderUsingState,
    ):
        return Validity(
            id=self.id,
            name=self.name,
            time_left=state["cooldown"].minimum_time_to_available(),
            valid=state["cooldown"].available
            and state["order_sword"].get_sword_count() > 0,
            cooldown_duration=self._is_valid(state),
        )

    def _is_valid(self, state: AdeleOrderUsingState):
        return (
            state["cooldown"].available and state["order_sword"].get_sword_count() > 0
        )


class AdeleRuinState(TypedDict):
    cooldown: Cooldown
    interval_state_first: Periodic
    interval_state_second: Periodic
    dynamics: Dynamics


class AdeleRuinComponentProps(TypedDict):
    id: str
    name: str
    periodic_interval_first: float
    periodic_damage_first: float
    periodic_hit_first: float
    lasting_duration_first: float
    periodic_interval_second: float
    periodic_damage_second: float
    periodic_hit_second: float
    lasting_duration_second: float
    cooldown_duration: float


class AdeleRuinComponent(
    Component,
):
    periodic_interval_first: float
    periodic_damage_first: float
    periodic_hit_first: float
    lasting_duration_first: float

    periodic_interval_second: float
    periodic_damage_second: float
    periodic_hit_second: float
    lasting_duration_second: float

    cooldown_duration: float
    delay: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "interval_state_first": Periodic(
                interval=self.periodic_interval_first,
                initial_counter=None,
            ),
            "interval_state_second": Periodic(
                interval=self.periodic_interval_second,
                initial_counter=self.lasting_duration_first,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> AdeleRuinComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "cooldown_duration": self.cooldown_duration,
            "periodic_interval_first": self.periodic_interval_first,
            "periodic_damage_first": self.periodic_damage_first,
            "periodic_hit_first": self.periodic_hit_first,
            "lasting_duration_first": self.lasting_duration_first,
            "periodic_interval_second": self.periodic_interval_second,
            "periodic_damage_second": self.periodic_damage_second,
            "periodic_hit_second": self.periodic_hit_second,
            "lasting_duration_second": self.lasting_duration_second,
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: AdeleRuinState,
    ):
        cooldown, interval_state_first, interval_state_second = (
            state["cooldown"].model_copy(),
            state["interval_state_first"].model_copy(),
            state["interval_state_second"].model_copy(),
        )

        cooldown.elapse(time)
        lapse_count_first = interval_state_first.elapse(time)
        lapse_count_second = interval_state_second.elapse(time)

        state["cooldown"] = cooldown
        state["interval_state_first"] = interval_state_first
        state["interval_state_second"] = interval_state_second

        return state, [EmptyEvent.elapsed(time)] + [
            EmptyEvent.dealt(self.periodic_damage_first, self.periodic_hit_first)
            for _ in range(lapse_count_first)
        ] + [
            EmptyEvent.dealt(self.periodic_damage_second, self.periodic_hit_second)
            for _ in range(lapse_count_second)
        ]

    @reducer_method
    def use(
        self,
        _: None,
        state: AdeleRuinState,
    ):
        cooldown, interval_state_first, interval_state_second = (
            state["cooldown"].model_copy(),
            state["interval_state_first"].model_copy(),
            state["interval_state_second"].model_copy(),
        )

        if not cooldown.available:
            return state, [EmptyEvent.rejected()]

        delay = self.delay

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        interval_state_first.set_time_left(time=self.lasting_duration_first)
        interval_state_second.set_time_left(
            time=self.lasting_duration_first + self.lasting_duration_second
        )

        state["cooldown"] = cooldown
        state["interval_state_first"] = interval_state_first
        state["interval_state_second"] = interval_state_second

        return state, [
            EmptyEvent.delayed(delay),
        ]

    @view_method
    def validity(
        self,
        state: AdeleRuinState,
    ):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(
        self,
        state: AdeleRuinState,
    ) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["interval_state_second"].time_left,
            lasting_duration=self.lasting_duration_first + self.lasting_duration_second,
        )


class AdeleRestoreState(TypedDict):
    lasting: RestoreLasting
    dynamics: Dynamics


class AdeleRestoreBuffComponent(Component):
    lasting_duration: float
    ether_multiplier: float
    stat: Stat

    delay: float

    def get_default_state(self):
        return {
            "lasting": RestoreLasting(
                time_left=0, ether_multiplier=self.ether_multiplier
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def use(self, _: None, state: AdeleRestoreState):
        lasting = state["lasting"].model_copy()

        lasting.set_time_left(
            state["dynamics"].stat.calculate_buff_duration(self.lasting_duration)
        )
        state["lasting"] = lasting

        return state, [EmptyEvent.delayed(self.delay)]

    @reducer_method
    def elapse(self, time: float, state: AdeleRestoreState):
        lasting = state["lasting"].model_copy()
        lasting.elapse(time)
        state["lasting"] = lasting

        return state, [EmptyEvent.elapsed(time)]

    @view_method
    def buff(self, state: AdeleRestoreState):
        if state["lasting"].enabled():
            return self.stat

        return None

    @view_method
    def running(self, state: AdeleRestoreState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["lasting"].time_left,
            lasting_duration=state["lasting"].assigned_duration,
        )


class AdeleStormState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    stack: Stack
    dynamics: Dynamics
    order_sword: OrderSword


class AdeleStormComponentProps(TypedDict):
    id: str
    name: str
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float
    maximum_stack: int
    delay: float
    cooldown_duration: float


class AdeleStormComponent(
    Component,
):
    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float
    maximum_stack: int
    delay: float
    cooldown_duration: float

    binds: dict[str, str] = {"order_sword": ".오더 VI.order_sword"}

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "stack": Stack(maximum_stack=self.maximum_stack),
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "order_sword": OrderSword(interval=self.periodic_interval),
        }

    def get_props(self) -> AdeleStormComponentProps:
        return {
            "id": self.id,
            "name": self.name,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "lasting_duration": self.lasting_duration,
            "maximum_stack": self.maximum_stack,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: AdeleStormState,
    ):
        return periodic_trait.elapse_periodic_with_cooldown(
            state,
            {"time": time},
            periodic_damage=self.periodic_damage,
            periodic_hit=self.periodic_hit * state["stack"].get_stack(),
        )

    @reducer_method
    def use(self, _: None, state: AdeleStormState):
        sword_count = state["order_sword"].get_sword_count()

        if sword_count <= 0:
            return state, [EmptyEvent.rejected()]

        state, events = periodic_trait.start_periodic_with_cooldown(
            state, {}, **self.get_props(), damage=0, hit=0
        )
        if not is_rejected(events):
            stack = state["stack"].model_copy()
            stack.reset(sword_count)
            state["stack"] = stack

        return state, events

    @view_method
    def validity(self, state: AdeleStormState):
        return Validity(
            id=self.id,
            name=self.name,
            time_left=state["cooldown"].minimum_time_to_available(),
            valid=state["cooldown"].available
            and state["order_sword"].get_sword_count() > 0,
            cooldown_duration=self.cooldown_duration,
        )

    @view_method
    def running(self, state: AdeleStormState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["periodic"].time_left,
            lasting_duration=self.lasting_duration,
            stack=state["stack"].stack,
        )
