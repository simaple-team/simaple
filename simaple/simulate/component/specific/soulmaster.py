from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.lasting_trait as lasting_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
import simaple.simulate.component.trait.simple_attack as simple_attack
from simaple.core.base import Stat
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import Cooldown, Lasting, LastingStack, Periodic
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.event import EmptyEvent
from simaple.simulate.global_property import Dynamics


class CosmicOrbState(TypedDict):
    orb: LastingStack
    cosmic_forge_lasting: Lasting


class CosmicOrb(Component):
    default_max_stack: int
    cosmic_forge_stack: int
    orb_lasting_duration: float

    stat: Stat

    def get_default_state(self):
        return {
            "orb": LastingStack(
                maximum_stack=self.cosmic_forge_stack,
                duration=self.orb_lasting_duration,
            ),
            "cosmic_forge_lasting": Lasting(time_left=0),
        }

    @reducer_method
    def increase(self, _: None, state: CosmicOrbState):
        orb = state["orb"].model_copy()

        orb.increase(1)
        if not state["cosmic_forge_lasting"].enabled():
            orb.increase(1)
        state["orb"] = orb

        state = self._regulate_if_no_cosmic_forge(state)
        return state, []

    @reducer_method
    def maximize(self, _: None, state: CosmicOrbState):
        orb = state["orb"].model_copy()
        orb.increase(10)
        state["orb"] = orb

        state = self._regulate_if_no_cosmic_forge(state)
        return state, []

    @view_method
    def buff(self, state: CosmicOrbState):
        if state["orb"].stack > 0:
            return self.stat

        return None

    def _regulate_if_no_cosmic_forge(self, state: CosmicOrbState) -> CosmicOrbState:
        if state["cosmic_forge_lasting"].enabled():
            return state

        orb = state["orb"].model_copy()
        orb.regulate(self.default_max_stack)
        state["orb"] = orb

        return state


class ElysionState(TypedDict):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics
    stack: LastingStack
    crack_cooldown: Cooldown


class ElysionProps(TypedDict):
    id: str
    name: str
    cooldown_duration: float
    delay: float
    lasting_duration: float
    crack_damage: float
    crack_hit: int
    crack_cooldown: float
    crack_duration: float
    maximum_crack_count: int


class Elysion(SkillComponent):
    cooldown_duration: float
    delay: float
    lasting_duration: float

    crack_damage: float
    crack_hit: int
    crack_cooldown: float
    crack_duration: float
    maximum_crack_count: int

    def get_default_state(self) -> ElysionState:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "stack": LastingStack(
                maximum_stack=self.maximum_crack_count, duration=self.crack_duration
            ),
            "crack_cooldown": Cooldown(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> ElysionProps:
        return {
            "id": self.id,
            "name": self.name,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "lasting_duration": self.lasting_duration,
            "crack_damage": self.crack_damage,
            "crack_hit": self.crack_hit,
            "crack_cooldown": self.crack_cooldown,
            "crack_duration": self.crack_duration,
            "maximum_crack_count": self.maximum_crack_count,
        }

    @reducer_method
    def crack(self, _: None, state: ElysionState):
        if not state["lasting"].enabled() or not state["crack_cooldown"].available:
            return state, []

        stack, crack_cooldown = (
            state["stack"].model_copy(),
            state["crack_cooldown"].model_copy(),
        )

        stack.increase()
        if stack.is_maximum():
            stack.reset()
            crack_cooldown.set_time_left(self.crack_cooldown)

            state["stack"] = stack
            state["crack_cooldown"] = crack_cooldown

            return state, [EmptyEvent.dealt(self.crack_damage, self.crack_hit)]

        state["stack"] = stack
        state["crack_cooldown"] = crack_cooldown

        return state, []

    @reducer_method
    def elapse(self, time: float, state: ElysionState):
        cooldown, lasting, crack_cooldown, stack = (
            state["cooldown"].model_copy(),
            state["lasting"].model_copy(),
            state["crack_cooldown"].model_copy(),
            state["stack"].model_copy(),
        )

        cooldown.elapse(time)
        lasting.elapse(time)
        crack_cooldown.elapse(time)
        stack.elapse(time)

        state["cooldown"] = cooldown
        state["lasting"] = lasting
        state["crack_cooldown"] = crack_cooldown
        state["stack"] = stack

        return state, [
            EmptyEvent.elapsed(time),
        ]

    @reducer_method
    def use(self, _: None, state: ElysionState):
        return lasting_trait.start_lasting_with_cooldown(
            state, self.cooldown_duration, self.lasting_duration, self.delay, False
        )

    @view_method
    def validity(self, state: ElysionState) -> Validity:
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: ElysionState) -> Running:
        return lasting_trait.running_view(state, self.name, self.id)


class CrossTheStyxState(TypedDict):
    elysion_lasting: Lasting


class CrossTheStyx(SkillComponent):
    name: str
    damage: float
    hit: float
    delay: float
    cooldown_duration: float = 0.0

    def get_default_state(self) -> CrossTheStyxState:
        return {
            "elysion_lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: CrossTheStyxState):
        if not state["elysion_lasting"].enabled():
            return state, [EmptyEvent.rejected()]

        return state, [
            EmptyEvent.dealt(self.damage, self.hit),
            EmptyEvent.delayed(self.delay),
        ]

    @view_method
    def validity(self, state: CrossTheStyxState):
        return Validity(
            id=self.id,
            name=self.name,
            time_left=0.0,
            valid=state["elysion_lasting"].enabled(),
            cooldown_duration=0.0,
        )


class CosmicBurstState(TypedDict):
    cooldown: Cooldown
    dynamics: Dynamics
    orb: LastingStack


class CosmicBurst(SkillComponent):
    damage: float
    hit: int
    delay: float
    cooldown_duration: float

    damage_decrement_after_2nd_hit: float  # 같은 대상 2번째 히트부터 70% 최종뎀 적용
    cooltime_reduce_per_orb: float  # 소비한 오브 1개당 재사용 1초 감소

    def get_default_state(self) -> CosmicBurstState:
        return {
            "cooldown": Cooldown(time_left=0.0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "orb": LastingStack(maximum_stack=5, duration=0.0),
        }

    @reducer_method
    def elapse(self, time: float, state: CosmicBurstState):
        cooldown = state["cooldown"].model_copy()
        cooldown.elapse(time)
        state["cooldown"] = cooldown

        return state, [EmptyEvent.elapsed(time)]

    @reducer_method
    def trigger(self, _: None, state: CosmicBurstState):
        if not state["cooldown"].available or state["orb"].stack == 0:
            return state, [EmptyEvent.rejected()]

        orb, cooldown = state["orb"], state["cooldown"].model_copy()
        orbs_stack_count = orb.stack

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
            - orbs_stack_count * self.cooltime_reduce_per_orb
        )
        orb.reset()

        damages = [EmptyEvent.dealt(self.damage, self.hit)]
        damages.append(
            EmptyEvent.dealt(
                self.damage * self.damage_decrement_after_2nd_hit,
                self.hit * (orbs_stack_count - 1),
            )
        )

        state["cooldown"] = cooldown
        state["orb"] = orb

        return state, damages


class CosmicShowerState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics
    orb: LastingStack


class CosmicShower(SkillComponent):
    name: str
    delay: float

    cooldown_duration: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    lasting_duration: float
    duration_increase_per_orb: float

    def get_default_state(self) -> CosmicShowerState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "orb": LastingStack(maximum_stack=5, duration=0.0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def elapse(self, time: float, state: CosmicShowerState):
        return periodic_trait.elapse_periodic_with_cooldown(
            state,
            time,
            self.periodic_damage,
            self.periodic_hit,
        )

    @reducer_method
    def use(self, _: None, state: CosmicShowerState):
        if not state["cooldown"].available or state["orb"].stack == 0:
            return state, [EmptyEvent.rejected()]

        orb, periodic, cooldown = (
            state["orb"].model_copy(),
            state["periodic"].model_copy(),
            state["cooldown"].model_copy(),
        )

        orbs_stack_count = orb.stack

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        periodic.set_time_left(
            self.lasting_duration + orbs_stack_count * self.duration_increase_per_orb
        )
        orb.reset()

        state["cooldown"] = cooldown
        state["periodic"] = periodic
        state["orb"] = orb

        return state, [EmptyEvent.delayed(self.delay)]

    @view_method
    def validity(self, state: CosmicShowerState):
        return Validity(
            id=self.id,
            name=self._get_name(),
            time_left=state["cooldown"].minimum_time_to_available(),
            valid=state["cooldown"].available and state["orb"].stack > 0,
            cooldown_duration=self.cooldown_duration,
        )

    @view_method
    def running(self, state: CosmicShowerState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["periodic"].time_left,
            lasting_duration=self.lasting_duration,
        )


class CosmosState(TypedDict):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics
    orb: LastingStack


class Cosmos(SkillComponent):
    name: str
    delay: float

    cooldown_duration: float

    periodic_initial_delay: Optional[float] = None
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    periodic_interval_decrement_per_orb: float

    lasting_duration: float

    def get_default_state(self) -> CosmosState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "orb": LastingStack(maximum_stack=5, duration=0.0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def elapse(self, time: float, state: CosmosState):
        return periodic_trait.elapse_periodic_with_cooldown(
            state,
            time,
            self.periodic_damage,
            self.periodic_hit,
        )

    @reducer_method
    def use(self, _: None, state: CosmosState):

        orb, periodic, cooldown = (
            state["orb"].model_copy(),
            state["periodic"].model_copy(),
            state["cooldown"].model_copy(),
        )

        if not cooldown.available or orb.stack == 0:
            return state, [EmptyEvent.rejected()]

        orbs_stack_count = orb.stack

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        periodic.interval = (
            self.periodic_interval
            - orbs_stack_count * self.periodic_interval_decrement_per_orb
        )
        periodic.set_time_left(self.lasting_duration)
        orb.reset()

        state["cooldown"] = cooldown
        state["periodic"] = periodic
        state["orb"] = orb

        return state, [EmptyEvent.delayed(self.delay)]

    @view_method
    def validity(self, state: CosmosState):
        return Validity(
            id=self.id,
            name=self._get_name(),
            time_left=state["cooldown"].minimum_time_to_available(),
            valid=state["cooldown"].available and state["orb"].stack > 0,
            cooldown_duration=self._get_cooldown_duration(),
        )

    @view_method
    def running(self, state: CosmosState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["periodic"].time_left,
            lasting_duration=self.lasting_duration,
        )


class FlareSlashState(TypedDict):
    cooldown: Cooldown
    dynamics: Dynamics


class FlareSlash(SkillComponent):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    cooldown_reduece_when_stance_changed: float
    cooldown_reduce_when_cross_the_styx_hit: float

    def get_default_state(self) -> FlareSlashState:
        return {
            "cooldown": Cooldown(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def elapse(self, time: float, state: FlareSlashState):
        return simple_attack.elapse(state, time)

    @reducer_method
    def change_stance_trigger(self, _: None, state: FlareSlashState):
        cooldown = state["cooldown"].model_copy()
        cooldown.reduce_by_value(self.cooldown_reduece_when_stance_changed)
        state["cooldown"] = cooldown

        return simple_attack.use_cooldown_attack(
            state, self.cooldown_duration, self.damage, self.hit, self.delay
        )

    @reducer_method
    def styx_trigger(self, _: None, state: FlareSlashState):
        cooldown = state["cooldown"].model_copy()
        cooldown.reduce_by_value(self.cooldown_reduce_when_cross_the_styx_hit)
        state["cooldown"] = cooldown
        return simple_attack.use_cooldown_attack(
            state, self.cooldown_duration, self.damage, self.hit, self.delay
        )

    @view_method
    def validity(self, state: FlareSlashState):
        return Validity(
            id=self.id,
            name=self._get_name(),
            time_left=state["cooldown"].minimum_time_to_available(),
            valid=False,
            cooldown_duration=self._get_cooldown_duration(),
        )
