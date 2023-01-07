from simaple.core.base import Stat
from simaple.simulate.base import Entity
from simaple.simulate.component.base import (
    Component,
    ReducerState,
    reducer_method,
    view_method,
)
from simaple.simulate.component.entity import Cooldown, Lasting, LastingStack, Periodic
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    BuffTrait,
    CooldownValidityTrait,
    PeriodicElapseTrait,
    UseSimpleAttackTrait,
)
from simaple.simulate.component.view import Running, Validity
from simaple.simulate.global_property import Dynamics


class CosmicOrbState(ReducerState):
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
            )
        }

    @reducer_method
    def increase(self, _: None, state: CosmicOrbState):
        state = state.deepcopy()
        state.orb.increase(1)
        if not state.cosmic_forge_lasting.enabled():
            state.orb.increase(1)

        state = self._regulate_if_no_cosmic_forge(state)
        return state, []

    @reducer_method
    def maximize(self, _: None, state: CosmicOrbState):
        state = state.deepcopy()
        state.orb.increase(10)
        state = self._regulate_if_no_cosmic_forge(state)
        return state, []

    @view_method
    def buff(self, state: CosmicOrbState):
        if state.orb.stack > 0:
            return self.stat

        return None

    def _regulate_if_no_cosmic_forge(self, state: CosmicOrbState) -> CosmicOrbState:
        if state.cosmic_forge_lasting.enabled():
            return state

        state = state.deepcopy()
        state.orb.regulate(self.default_max_stack)

        return state


class ElysionState(ReducerState):
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics
    stack: LastingStack
    crack_cooldown: Cooldown


class Elysion(SkillComponent, BuffTrait, CooldownValidityTrait):
    cooldown_duration: float
    delay: float
    lasting_duration: float

    crack_damage: float
    crack_hit: int
    crack_cooldown: float
    crack_duration: float
    maximum_crack_count: int

    def get_default_state(self) -> dict[str, Entity]:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "stack": LastingStack(
                maximum_stack=self.maximum_crack_count, duration=self.crack_duration
            ),
            "crack_cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def crack(self, _: None, state: ElysionState):
        if not state.lasting.enabled() or not state.crack_cooldown.available:
            return state, []

        state = state.deepcopy()
        state.stack.increase()
        if state.stack.is_maximum():
            state.stack.reset()
            state.crack_cooldown.set_time_left(self.crack_cooldown)
            return state, [self.event_provider.dealt(self.crack_damage, self.crack_hit)]

        return state, []

    @reducer_method
    def elapse(self, time: float, state: ElysionState):
        state = state.deepcopy()

        state.cooldown.elapse(time)
        state.lasting.elapse(time)
        state.crack_cooldown.elapse(time)
        state.stack.elapse(time)

        return state, [
            self.event_provider.elapsed(time),
        ]

    @reducer_method
    def use(self, _: None, state: ElysionState):
        return self.use_buff_trait(state)

    @view_method
    def validity(self, state: ElysionState) -> Validity:
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: ElysionState) -> Running:
        return self.running_in_buff_trait(state)

    def _get_lasting_duration(self, state: ElysionState) -> float:
        return self.lasting_duration


class CrossTheStyxState(ReducerState):
    elysion_lasting: Lasting


class CrossTheStyx(SkillComponent):
    name: str
    damage: float
    hit: float
    delay: float
    cooldown_duration: float = 0.0

    def get_default_state(self):
        return {}

    @reducer_method
    def use(self, _: None, state: CrossTheStyxState):
        if not state.elysion_lasting.enabled():
            return state, [self.event_provider.rejected()]

        return state, [
            self.event_provider.dealt(self.damage, self.hit),
            self.event_provider.delayed(self.delay),
        ]

    @view_method
    def validity(self, state: CrossTheStyxState):
        return Validity(
            name=self.name,
            time_left=0.0,
            valid=state.elysion_lasting.enabled(),
            cooldown_duration=0.0,
        )


class CosmicBurstState(ReducerState):
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

    def get_default_state(self) -> dict[str, Entity]:
        return {"cooldown": Cooldown(time_left=0.0)}

    @reducer_method
    def elapse(self, time: float, state: CosmicBurstState):
        state = state.deepcopy()
        state.cooldown.elapse(time)

        return state, [self.event_provider.elapsed(time)]

    @reducer_method
    def trigger(self, _: None, state: CosmicBurstState):
        if not state.cooldown.available or state.orb.stack == 0:
            return state, [self.event_provider.rejected()]

        state = state.deepcopy()
        orbs = state.orb.stack

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
            - orbs * self.cooltime_reduce_per_orb
        )
        state.orb.reset()

        damages = [self.event_provider.dealt(self.damage, self.hit)]
        damages.append(
            self.event_provider.dealt(
                self.damage * self.damage_decrement_after_2nd_hit, self.hit * (orbs - 1)
            )
        )

        return state, damages


class CosmicShowerState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics
    orb: LastingStack


class CosmicShower(SkillComponent, PeriodicElapseTrait, CooldownValidityTrait):
    name: str
    delay: float

    cooldown_duration: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float

    lasting_duration: float
    duration_increase_per_orb: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: CosmicShowerState):
        return self.elapse_periodic_damage_trait(time, state)

    @reducer_method
    def use(self, _: None, state: CosmicShowerState):
        state = state.deepcopy()
        if not state.cooldown.available or state.orb.stack == 0:
            return state, [self.event_provider.rejected()]

        orbs = state.orb.stack
        delay = self._get_delay()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )
        state.periodic.set_time_left(
            self._get_lasting_duration(state) + orbs * self.duration_increase_per_orb
        )
        state.orb.reset()

        return state, [self.event_provider.delayed(delay)]

    @view_method
    def validity(self, state: CosmicShowerState):
        return Validity(
            name=self._get_name(),
            time_left=max(0, state.cooldown.time_left),
            valid=state.cooldown.available and state.orb.stack > 0,
            cooldown_duration=self._get_cooldown_duration(),
        )

    @view_method
    def running(self, state: CosmicShowerState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: CosmicShowerState) -> float:
        return self.lasting_duration

    def _get_periodic_damage_hit(self, state: CosmicShowerState) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit


class CosmosState(ReducerState):
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics
    orb: LastingStack


class Cosmos(SkillComponent, PeriodicElapseTrait, CooldownValidityTrait):
    name: str
    delay: float

    cooldown_duration: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    periodic_interval_decrement_per_orb: float

    lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: CosmosState):
        return self.elapse_periodic_damage_trait(time, state)

    @reducer_method
    def use(self, _: None, state: CosmosState):
        state = state.deepcopy()
        if not state.cooldown.available or state.orb.stack == 0:
            return state, [self.event_provider.rejected()]

        orbs = state.orb.stack
        delay = self._get_delay()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self._get_cooldown_duration())
        )
        state.periodic.interval = (
            self.periodic_interval - orbs * self.periodic_interval_decrement_per_orb
        )
        state.periodic.set_time_left(self._get_lasting_duration(state))
        state.orb.reset()

        return state, [self.event_provider.delayed(delay)]

    @view_method
    def validity(self, state: CosmosState):
        return Validity(
            name=self._get_name(),
            time_left=max(0, state.cooldown.time_left),
            valid=state.cooldown.available and state.orb.stack > 0,
            cooldown_duration=self._get_cooldown_duration(),
        )

    @view_method
    def running(self, state: CosmosState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: CosmosState) -> float:
        return self.lasting_duration

    def _get_periodic_damage_hit(self, state: CosmosState) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit


class FlareSlashState(ReducerState):
    cooldown: Cooldown
    dynamics: Dynamics


class FlareSlash(SkillComponent, UseSimpleAttackTrait):
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    cooldown_reduece_when_stance_changed: float
    cooldown_reduce_when_cross_the_styx_hit: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
        }

    @reducer_method
    def elapse(self, time: float, state: FlareSlashState):
        return self.elapse_simple_attack(time, state)

    @reducer_method
    def change_stance_trigger(self, _: None, state: FlareSlashState):
        state = state.deepcopy()
        state.cooldown.time_left -= self.cooldown_reduece_when_stance_changed
        return self.use_simple_attack(state)

    @reducer_method
    def styx_trigger(self, _: None, state: FlareSlashState):
        state = state.deepcopy()
        state.cooldown.time_left -= self.cooldown_reduce_when_cross_the_styx_hit
        return self.use_simple_attack(state)

    @view_method
    def validity(self, state: FlareSlashState):
        return Validity(
            name=self._get_name(),
            time_left=max(0, state.cooldown.time_left),
            valid=False,
            cooldown_duration=self._get_cooldown_duration(),
        )

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit
