from typing import Optional, TypedDict

import simaple.simulate.component.trait.common.consumable_trait as consumable_trait
import simaple.simulate.component.trait.common.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.common.lasting_trait as lasting_trait
import simaple.simulate.component.trait.common.periodic_trait as periodic_trait
from simaple.core import Stat
from simaple.simulate.component.base import (
    Component,
    ReducerState,
    reducer_method,
    view_method,
)
from simaple.simulate.component.entity import (
    Cooldown,
    Cycle,
    Keydown,
    Lasting,
    Periodic,
)
from simaple.simulate.component.skill import SkillComponent
from simaple.simulate.component.trait.impl import (
    BuffTrait,
    CooldownValidityTrait,
    KeydownSkillTrait,
    PeriodicWithSimpleDamageTrait,
    UsePeriodicDamageTrait,
)
from simaple.simulate.component.util import is_keydown_ended
from simaple.simulate.component.view import Running
from simaple.simulate.core.base import Entity, Event
from simaple.simulate.event import DelayPayload, EmptyEvent
from simaple.simulate.global_property import Dynamics


class RobotMastery(Entity):
    summon_increment: float
    robot_damage_increment: float

    def get_summon_multiplier(self) -> float:
        return 1 + self.summon_increment / 100

    def get_robot_modifier(self) -> Stat:
        return Stat(final_damage_multiplier=self.robot_damage_increment)


class RobotMasteryComponent(Component):
    summon_increment: float
    robot_damage_increment: float

    def get_default_state(self):
        return {
            "robot_mastery": RobotMastery(
                summon_increment=self.summon_increment,
                robot_damage_increment=self.robot_damage_increment,
            )
        }


class RobotSetupBuffState(TypedDict):
    robot_mastery: RobotMastery
    cooldown: Cooldown
    lasting: Lasting
    dynamics: Dynamics


class RobotSetupBuff(SkillComponent):
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    binds: dict[str, str] = {"robot_mastery": ".로봇 마스터리.robot_mastery"}

    def get_default_state(self) -> RobotSetupBuffState:
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
            "robot_mastery": RobotMastery(summon_increment=0, robot_damage_increment=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: RobotSetupBuffState,
    ):
        return lasting_trait.start_lasting_with_cooldown(
            state,
            self.cooldown_duration,
            self._get_lasting_duration(state),
            self.delay,
            False,
        )

    @view_method
    def buff(self, state: RobotSetupBuffState) -> Optional[Stat]:
        if state["lasting"].enabled():
            return self.stat

        return None

    @reducer_method
    def elapse(self, time: float, state: RobotSetupBuffState):
        return lasting_trait.elapse_lasting_with_cooldown(state, time)

    @view_method
    def validity(self, state: RobotSetupBuffState):
        return cooldown_trait.validity_view(
            state, self.id, self.name, self.cooldown_duration
        )

    @view_method
    def running(self, state: RobotSetupBuffState) -> Running:
        return lasting_trait.running_view(state, self.id, self.name)

    def _get_lasting_duration(self, state: RobotSetupBuffState) -> float:
        return self.lasting_duration * state["robot_mastery"].get_summon_multiplier()


class RobotSummonState(TypedDict):
    robot_mastery: RobotMastery
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class RobotSummonSkill(
    SkillComponent,
):
    binds: dict[str, str] = {"robot_mastery": ".로봇 마스터리.robot_mastery"}
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    periodic_initial_delay: float
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    def get_default_state(self) -> RobotSummonState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "robot_mastery": RobotMastery(summon_increment=0, robot_damage_increment=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    @reducer_method
    def elapse(self, time: float, state: RobotSummonState):
        cooldown, periodic = (
            state["cooldown"].model_copy(),
            state["periodic"].model_copy(),
        )

        cooldown.elapse(time)
        lapse_count = periodic.elapse(time)

        state["cooldown"] = cooldown
        state["periodic"] = periodic

        return state, [EmptyEvent.elapsed(time)] + [
            EmptyEvent.dealt(
                self.periodic_damage,
                self.periodic_hit,
                modifier=state["robot_mastery"].get_robot_modifier(),
            )
            for _ in range(lapse_count)
        ]

    @reducer_method
    def use(self, _: None, state: RobotSummonState):
        return periodic_trait.start_periodic_with_cooldown(
            state,
            self.damage,
            self.hit,
            self.delay,
            self.cooldown_duration,
            self._get_lasting_duration(state),
        )

    @view_method
    def validity(self, state: RobotSummonState):
        return cooldown_trait.validity_view(
            state, self.id, self.name, self.cooldown_duration
        )

    @view_method
    def running(self, state: RobotSummonState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["periodic"].time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: RobotSummonState) -> float:
        return self.lasting_duration * state["robot_mastery"].get_summon_multiplier()


class HommingMissileState(TypedDict):
    bomber_time: Lasting
    full_barrage_keydown: Keydown
    full_barrage_penalty_lasting: Lasting
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class HommingMissile(SkillComponent):
    binds: dict[str, str] = {
        "bomber_time": ".봄버 타임.lasting",
        "full_barrage_keydown": ".메탈아머 전탄발사.keydown",
        "full_barrage_penalty_lasting": ".메탈아머 전탄발사.penalty_lasting",
    }
    name: str
    cooldown_duration: float
    delay: float

    periodic_initial_delay: float
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    final_damage_multiplier_during_barrage: float

    def get_default_state(self) -> HommingMissileState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
        }

    @reducer_method
    def use(self, _: None, state: HommingMissileState):
        return periodic_trait.start_periodic_with_cooldown(
            state,
            0,
            0,
            self.delay,
            self.cooldown_duration,
            self.lasting_duration,
        )

    @reducer_method
    def elapse(
        self,
        time: float,
        state: HommingMissileState,
    ):
        cooldown, periodic = (
            state["cooldown"].model_copy(),
            state["periodic"].model_copy(),
        )

        cooldown.elapse(time)
        lapse_count = periodic.elapse(time)

        state["cooldown"] = cooldown
        state["periodic"] = periodic

        return state, [EmptyEvent.elapsed(time)] + [
            EmptyEvent.dealt(
                self.periodic_damage,
                self.get_homming_missile_hit(state),
                (
                    Stat(
                        final_damage_multiplier=self.final_damage_multiplier_during_barrage
                    )
                    if state["full_barrage_keydown"].running
                    else None
                ),
            )
            for _ in range(lapse_count)
        ]

    @reducer_method
    def pause(self, payload: DelayPayload, state: HommingMissileState):
        periodic = state["periodic"].model_copy()
        periodic.set_interval_counter(payload.time)
        state["periodic"] = periodic

        return state, []

    def get_homming_missile_hit(self, state: HommingMissileState) -> int:
        hit = int(self.periodic_hit)
        if state["bomber_time"].enabled():
            hit += 6

        if state["full_barrage_keydown"].running:
            hit += 7

        if state["full_barrage_penalty_lasting"].enabled():
            hit = 0

        return hit

    @view_method
    def validity(self, state: HommingMissileState):
        return cooldown_trait.validity_view(
            state, self.id, self.name, self.cooldown_duration
        )

    @view_method
    def running(self, state: HommingMissileState) -> Running:
        return periodic_trait.running_view(
            state, self.id, self.name, self.lasting_duration
        )


class FullMetalBarrageState(ReducerState):
    cooldown: Cooldown
    keydown: Keydown
    penalty_lasting: Lasting
    dynamics: Dynamics


class FullMetalBarrageComponent(
    SkillComponent, KeydownSkillTrait, CooldownValidityTrait
):
    maximum_keydown_time: float

    damage: float
    hit: float
    delay: float
    cooldown_duration: float

    keydown_prepare_delay: float
    keydown_end_delay: float

    homing_penalty_duration: float
    homing_final_damage_multiplier: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "keydown": Keydown(interval=self.delay, running=False),
            "penalty_lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: FullMetalBarrageState,
    ):
        return self.use_keydown_trait(state)

    @reducer_method
    def elapse(self, time: float, state: FullMetalBarrageState):
        state.penalty_lasting.elapse(time)
        state, event = self.elapse_keydown_trait(time, state)

        if is_keydown_ended(event):
            state.penalty_lasting.set_time_left(self.homing_penalty_duration)

        return state, event

    @reducer_method
    def stop(self, _, state: FullMetalBarrageState):
        state, event = self.stop_keydown_trait(state)

        if is_keydown_ended(event):
            state.penalty_lasting.set_time_left(self.homing_penalty_duration)

        return state, event

    @view_method
    def validity(self, state: FullMetalBarrageState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def keydown(self, state: FullMetalBarrageState):
        return self.keydown_view_in_keydown_trait(state)

    def _get_maximum_keydown_time_prepare_delay(self) -> tuple[float, float]:
        return self.maximum_keydown_time, self.keydown_prepare_delay

    def _get_keydown_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_keydown_end_damage_hit_delay(self) -> tuple[float, float, float]:
        return 0, 0, self.keydown_end_delay


class MultipleOptionState(ReducerState):
    cycle: Cycle
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics
    robot_mastery: RobotMastery


class MultipleOptionComponent(SkillComponent, CooldownValidityTrait):
    name: str
    cooldown_duration: float
    delay: float

    periodic_initial_delay: float
    periodic_interval: float
    lasting_duration: float

    missile_count: int
    missile_damage: float
    missile_hit: int

    gatling_count: int
    gatling_damage: float
    gatling_hit: int

    binds: dict[str, str] = {"robot_mastery": ".로봇 마스터리.robot_mastery"}

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "cycle": Cycle(tick=0, period=self.missile_count + self.gatling_count),
        }

    def get_damage_event(
        self,
        state: MultipleOptionState,
    ) -> Event:
        if state.cycle.get_tick() < self.missile_count:
            return EmptyEvent.dealt(
                self.missile_damage,
                self.missile_hit,
                modifier=state.robot_mastery.get_robot_modifier(),
            )

        return EmptyEvent.dealt(
            self.gatling_damage,
            self.gatling_hit,
            modifier=state.robot_mastery.get_robot_modifier(),
        )

    @reducer_method
    def elapse(self, time: float, state: MultipleOptionState):
        state = state.deepcopy()

        state.cooldown.elapse(time)
        dealing_events = []

        for _ in range(state.periodic.elapse(time)):
            dealing_events.append(self.get_damage_event(state))
            state.cycle.step()

        return state, [EmptyEvent.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: MultipleOptionState):
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, EmptyEvent.rejected()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
        )
        state.periodic.set_time_left(self.lasting_duration)
        state.cycle.clear()

        return state, [
            EmptyEvent.delayed(self.delay),
        ]

    @view_method
    def validity(self, state: MultipleOptionState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: MultipleOptionState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: MultipleOptionState) -> float:
        return self.lasting_duration


class DynamicIntervalPeriodic(Entity):
    interval_counter: float = 0.0
    interval: float
    time_left: float = 0.0
    count: int = 0
    count_interval_penalty: float
    max_count: int

    def set_time_left(self, time: float, count: int):
        self.time_left = time
        self.interval_counter = 0
        self.count = count

    def enabled(self):
        return self.time_left > 0

    def resolving(self, time: float):
        self.interval_counter -= min(time, self.time_left)
        self.time_left -= time
        elapse_count = 0

        while self.interval_counter <= 0:
            self.interval_counter += (
                self.interval + self.count * self.count_interval_penalty
            )
            elapse_count += 1
            yield self.count
            self.count += 1
            self.count = min(self.max_count, self.count)

    def disable(self):
        self.time_left = 0


class MecaCarrierState(ReducerState):
    cooldown: Cooldown
    periodic: DynamicIntervalPeriodic
    dynamics: Dynamics
    robot_mastery: RobotMastery


class MecaCarrier(SkillComponent, CooldownValidityTrait):
    name: str
    cooldown_duration: float
    delay: float
    lasting_duration: float

    periodic_interval: float

    maximum_intercepter: int
    start_intercepter: int
    damage_per_intercepter: float
    hit_per_intercepter: int
    intercepter_penalty: float

    binds: dict[str, str] = {"robot_mastery": ".로봇 마스터리.robot_mastery"}

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": DynamicIntervalPeriodic(
                interval=self.periodic_interval,
                time_left=0,
                count=self.start_intercepter,
                count_interval_penalty=self.intercepter_penalty,
                max_count=self.maximum_intercepter,
            ),
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: MecaCarrierState,
    ):
        state = state.deepcopy()
        state.cooldown.elapse(time)

        dealing_events = []

        for intercepter_count in state.periodic.resolving(time):
            for _ in range(intercepter_count):
                dealing_events.append(
                    EmptyEvent.dealt(
                        self.damage_per_intercepter,
                        self.hit_per_intercepter,
                        modifier=state.robot_mastery.get_robot_modifier(),
                    )
                )

        return state, [EmptyEvent.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: MecaCarrierState):
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, EmptyEvent.rejected()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
        )

        state.periodic.set_time_left(self.lasting_duration, self.start_intercepter)

        return state, [
            EmptyEvent.delayed(self.delay),
        ]

    @view_method
    def validity(self, state: MecaCarrierState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: MecaCarrierState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state.periodic.time_left,
            stack=state.periodic.count if state.periodic.time_left > 0 else 0,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: MecaCarrierState) -> float:
        return self.lasting_duration
