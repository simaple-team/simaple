from typing import Optional, TypedDict

import simaple.simulate.component.trait.cooldown_trait as cooldown_trait
import simaple.simulate.component.trait.keydown_trait as keydown_trait
import simaple.simulate.component.trait.lasting_trait as lasting_trait
import simaple.simulate.component.trait.periodic_trait as periodic_trait
from simaple.core import Stat
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.entity import (
    Cooldown,
    Cycle,
    Keydown,
    Lasting,
    Periodic,
)
from simaple.simulate.component.skill import SkillComponent
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


class RobotSetupBuffProps(TypedDict):
    id: str
    name: str
    cooldown_duration: float
    delay: float
    lasting_duration: float
    stat: Stat


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

    def get_props(self) -> RobotSetupBuffProps:
        return {
            "id": self.id,
            "name": self.name,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "lasting_duration": self.lasting_duration,
            "stat": self.stat,
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: RobotSetupBuffState,
    ):
        return lasting_trait.start_lasting_with_cooldown(
            state,
            {},
            **self.get_props(),
            apply_buff_duration=False,
        )

    @view_method
    def buff(self, state: RobotSetupBuffState) -> Optional[Stat]:
        if state["lasting"].enabled():
            return self.stat

        return None

    @reducer_method
    def elapse(self, time: float, state: RobotSetupBuffState):
        return lasting_trait.elapse_lasting_with_cooldown(
            state, {"time": time}, **self.get_props()
        )

    @view_method
    def validity(self, state: RobotSetupBuffState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: RobotSetupBuffState) -> Running:
        return lasting_trait.running_view(state, **self.get_props())

    def _get_lasting_duration(self, state: RobotSetupBuffState) -> float:
        return self.lasting_duration * state["robot_mastery"].get_summon_multiplier()


class RobotSummonState(TypedDict):
    robot_mastery: RobotMastery
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class RobotSummonProps(TypedDict):
    id: str
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

    def get_props(self) -> RobotSummonProps:
        return {
            "id": self.id,
            "name": self.name,
            "damage": self.damage,
            "hit": self.hit,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "lasting_duration": self.lasting_duration,
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
        return cooldown_trait.validity_view(state, **self.get_props())

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


class HommingMissileProps(TypedDict):
    id: str
    name: str
    cooldown_duration: float
    delay: float
    periodic_initial_delay: float
    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float
    final_damage_multiplier_during_barrage: float


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
            "bomber_time": Lasting(time_left=0),
            "full_barrage_keydown": Keydown(interval=0),
            "full_barrage_penalty_lasting": Lasting(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> HommingMissileProps:
        return {
            "id": self.id,
            "name": self.name,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "periodic_damage": self.periodic_damage,
            "periodic_hit": self.periodic_hit,
            "lasting_duration": self.lasting_duration,
            "final_damage_multiplier_during_barrage": self.final_damage_multiplier_during_barrage,
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
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: HommingMissileState) -> Running:
        return periodic_trait.running_view(
            state, self.id, self.name, self.lasting_duration
        )


class FullMetalBarrageState(TypedDict):
    cooldown: Cooldown
    keydown: Keydown
    penalty_lasting: Lasting
    dynamics: Dynamics


class FullMetalBarrageProps(TypedDict):
    id: str
    name: str
    maximum_keydown_time: float
    damage: float
    hit: float
    delay: float
    cooldown_duration: float
    keydown_prepare_delay: float
    keydown_end_delay: float
    homing_penalty_duration: float
    homing_final_damage_multiplier: float


class FullMetalBarrageComponent(
    SkillComponent,
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

    def get_default_state(self) -> FullMetalBarrageState:
        return {
            "cooldown": Cooldown(time_left=0),
            "keydown": Keydown(interval=self.delay),
            "penalty_lasting": Lasting(time_left=0),
            "dynamics": Dynamics.model_validate({"stat": {}}),
        }

    def get_props(self) -> FullMetalBarrageProps:
        return {
            "id": self.id,
            "name": self.name,
            "maximum_keydown_time": self.maximum_keydown_time,
            "damage": self.damage,
            "hit": self.hit,
            "delay": self.delay,
            "cooldown_duration": self.cooldown_duration,
            "keydown_prepare_delay": self.keydown_prepare_delay,
            "keydown_end_delay": self.keydown_end_delay,
            "homing_penalty_duration": self.homing_penalty_duration,
            "homing_final_damage_multiplier": self.homing_final_damage_multiplier,
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: FullMetalBarrageState,
    ):
        return keydown_trait.use_keydown(
            state,
            self.maximum_keydown_time,
            self.keydown_prepare_delay,
            self.cooldown_duration,
        )

    @reducer_method
    def elapse(self, time: float, state: FullMetalBarrageState):

        state, event = keydown_trait.elapse_keydown(
            state, time, self.damage, self.hit, 0, 0, self.keydown_end_delay
        )

        penalty_lasting = state["penalty_lasting"].model_copy()
        penalty_lasting.elapse(time)

        if is_keydown_ended(event):
            penalty_lasting.set_time_left(self.homing_penalty_duration)

        state["penalty_lasting"] = penalty_lasting

        return state, event

    @reducer_method
    def stop(self, _, state: FullMetalBarrageState):
        state, event = keydown_trait.stop_keydown(state, 0, 0, self.keydown_end_delay)

        penalty_lasting = state["penalty_lasting"].model_copy()
        if is_keydown_ended(event):
            penalty_lasting.set_time_left(self.homing_penalty_duration)

        state["penalty_lasting"] = penalty_lasting

        return state, event

    @view_method
    def validity(self, state: FullMetalBarrageState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def keydown(self, state: FullMetalBarrageState):
        return keydown_trait.keydown_view(state, self.name)


class MultipleOptionState(TypedDict):
    cycle: Cycle
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics
    robot_mastery: RobotMastery


class MultipleOptionProps(TypedDict):
    id: str
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


class MultipleOptionComponent(SkillComponent):
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

    def get_default_state(self) -> MultipleOptionState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(
                interval=self.periodic_interval,
                initial_counter=self.periodic_initial_delay,
                time_left=0,
            ),
            "cycle": Cycle(tick=0, period=self.missile_count + self.gatling_count),
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "robot_mastery": RobotMastery(summon_increment=0, robot_damage_increment=0),
        }

    def get_props(self) -> MultipleOptionProps:
        return {
            "id": self.id,
            "name": self.name,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "periodic_initial_delay": self.periodic_initial_delay,
            "periodic_interval": self.periodic_interval,
            "lasting_duration": self.lasting_duration,
            "missile_count": self.missile_count,
            "missile_damage": self.missile_damage,
            "missile_hit": self.missile_hit,
            "gatling_count": self.gatling_count,
            "gatling_damage": self.gatling_damage,
            "gatling_hit": self.gatling_hit,
        }

    def get_damage_event(self, cycle: Cycle, robot_mastery: RobotMastery) -> Event:
        if cycle.get_tick() < self.missile_count:
            return EmptyEvent.dealt(
                self.missile_damage,
                self.missile_hit,
                modifier=robot_mastery.get_robot_modifier(),
            )

        return EmptyEvent.dealt(
            self.gatling_damage,
            self.gatling_hit,
            modifier=robot_mastery.get_robot_modifier(),
        )

    @reducer_method
    def elapse(self, time: float, state: MultipleOptionState):
        cooldown, cycle, periodic = (
            state["cooldown"].model_copy(),
            state["cycle"].model_copy(),
            state["periodic"].model_copy(),
        )

        cooldown.elapse(time)
        dealing_events = []

        for _ in range(periodic.elapse(time)):
            dealing_events.append(self.get_damage_event(cycle, state["robot_mastery"]))
            cycle.step()

        state["cooldown"] = cooldown
        state["cycle"] = cycle
        state["periodic"] = periodic

        return state, [EmptyEvent.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: MultipleOptionState):
        if not state["cooldown"].available:
            return state, [EmptyEvent.rejected()]

        cooldown, cycle, periodic = (
            state["cooldown"].model_copy(),
            state["cycle"].model_copy(),
            state["periodic"].model_copy(),
        )

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )
        periodic.set_time_left(self.lasting_duration)
        cycle.clear()

        state["cooldown"] = cooldown
        state["cycle"] = cycle
        state["periodic"] = periodic

        return state, [
            EmptyEvent.delayed(self.delay),
        ]

    @view_method
    def validity(self, state: MultipleOptionState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: MultipleOptionState) -> Running:
        return periodic_trait.running_view(
            state, self.id, self.name, self.lasting_duration
        )


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


class MecaCarrierState(TypedDict):
    cooldown: Cooldown
    periodic: DynamicIntervalPeriodic
    dynamics: Dynamics
    robot_mastery: RobotMastery


class MecaCarrierProps(TypedDict):
    id: str
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


class MecaCarrier(SkillComponent):
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

    def get_default_state(self) -> MecaCarrierState:
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": DynamicIntervalPeriodic(
                interval=self.periodic_interval,
                time_left=0,
                count=self.start_intercepter,
                count_interval_penalty=self.intercepter_penalty,
                max_count=self.maximum_intercepter,
            ),
            "dynamics": Dynamics.model_validate({"stat": {}}),
            "robot_mastery": RobotMastery(summon_increment=0, robot_damage_increment=0),
        }

    def get_props(self) -> MecaCarrierProps:
        return {
            "id": self.id,
            "name": self.name,
            "cooldown_duration": self.cooldown_duration,
            "delay": self.delay,
            "lasting_duration": self.lasting_duration,
            "periodic_interval": self.periodic_interval,
            "maximum_intercepter": self.maximum_intercepter,
            "start_intercepter": self.start_intercepter,
            "damage_per_intercepter": self.damage_per_intercepter,
            "hit_per_intercepter": self.hit_per_intercepter,
            "intercepter_penalty": self.intercepter_penalty,
        }

    @reducer_method
    def elapse(
        self,
        time: float,
        state: MecaCarrierState,
    ):
        cooldown = state["cooldown"].model_copy()
        periodic = state["periodic"].model_copy()

        cooldown.elapse(time)

        dealing_events = []

        for intercepter_count in periodic.resolving(time):
            for _ in range(intercepter_count):
                dealing_events.append(
                    EmptyEvent.dealt(
                        self.damage_per_intercepter,
                        self.hit_per_intercepter,
                        modifier=state["robot_mastery"].get_robot_modifier(),
                    )
                )

        state["cooldown"] = cooldown
        state["periodic"] = periodic

        return state, [EmptyEvent.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: MecaCarrierState):
        if not state["cooldown"].available:
            return state, [EmptyEvent.rejected()]

        cooldown = state["cooldown"].model_copy()
        periodic = state["periodic"].model_copy()

        cooldown.set_time_left(
            state["dynamics"].stat.calculate_cooldown(self.cooldown_duration)
        )

        periodic.set_time_left(self.lasting_duration, self.start_intercepter)

        state["cooldown"] = cooldown
        state["periodic"] = periodic

        return state, [
            EmptyEvent.delayed(self.delay),
        ]

    @view_method
    def validity(self, state: MecaCarrierState):
        return cooldown_trait.validity_view(state, **self.get_props())

    @view_method
    def running(self, state: MecaCarrierState) -> Running:
        return Running(
            id=self.id,
            name=self.name,
            time_left=state["periodic"].time_left,
            stack=state["periodic"].count if state["periodic"].time_left > 0 else 0,
            lasting_duration=self.lasting_duration,
        )
