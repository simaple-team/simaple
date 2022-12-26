from typing import Optional

from simaple.core import Stat
from simaple.simulate.base import Entity, Event
from simaple.simulate.component.base import (
    Component,
    ReducerState,
    reducer_method,
    view_method,
)
from simaple.simulate.component.entity import Cycle
from simaple.simulate.component.keydown_skill import Keydown
from simaple.simulate.component.skill import (
    Cooldown,
    Duration,
    Periodic,
    SkillComponent,
)
from simaple.simulate.component.trait.impl import (
    CooldownValidityTrait,
    DurableTrait,
    StartIntervalWithoutDamageTrait,
    TickEmittingTrait,
)
from simaple.simulate.component.view import Running
from simaple.simulate.global_property import Dynamics


class RobotMastery(Entity):
    summon_increment: float
    robot_damage_increment: float
    robot_buff_damage_multiplier: float

    def get_summon_multiplier(self) -> float:
        return 1 + self.summon_increment / 100

    def get_robot_modifier(self) -> Stat:
        return Stat(final_damage_multiplier=self.robot_damage_increment)

    def get_robot_buff(self) -> Stat:
        return Stat(damage_multiplier=self.robot_buff_damage_multiplier)


class RobotMasteryComponent(Component):
    summon_increment: float
    robot_damage_increment: float
    robot_buff_damage_multiplier: float

    def get_default_state(self):
        return {
            "robot_mastery": RobotMastery(
                summon_increment=self.summon_increment,
                robot_damage_increment=self.robot_damage_increment,
                robot_buff_damage_multiplier=self.robot_buff_damage_multiplier,
            )
        }


class RobotSetupBuffState(ReducerState):
    robot_mastery: RobotMastery
    cooldown: Cooldown
    duration: Duration
    dynamics: Dynamics


class RobotSetupBuff(SkillComponent, DurableTrait, CooldownValidityTrait):
    stat: Stat
    cooldown: float
    delay: float
    duration: float
    binds: dict[str, str] = {"robot_mastery": ".로봇 마스터리.robot_mastery"}

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "duration": Duration(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: RobotSetupBuffState,
    ):
        return self.use_durable_trait(state)

    @reducer_method
    def elapse(self, time: float, state: RobotSetupBuffState):
        return self.elapse_durable_trait(time, state)

    @view_method
    def validity(self, state: RobotSetupBuffState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def buff(self, state: RobotSetupBuffState) -> Optional[Stat]:
        if state.duration.enabled():
            return self.stat + state.robot_mastery.get_robot_buff()

        return None

    @view_method
    def running(self, state: RobotSetupBuffState) -> Running:
        return Running(
            name=self.name,
            time_left=state.duration.time_left,
            duration=self._get_duration(state),
        )

    def _get_duration(self, state: RobotSetupBuffState) -> float:
        return self.duration * state.robot_mastery.get_summon_multiplier()


class RobotSummonState(ReducerState):
    robot_mastery: RobotMastery
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class RobotSummonSkill(SkillComponent, TickEmittingTrait, CooldownValidityTrait):
    binds: dict[str, str] = {"robot_mastery": ".로봇 마스터리.robot_mastery"}
    name: str
    damage: float
    hit: float
    cooldown: float
    delay: float

    tick_interval: float
    tick_damage: float
    tick_hit: float
    duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.tick_interval, time_left=0),
        }

    @view_method
    def buff(self, state: RobotSummonState):
        if not state.periodic.enabled():
            return None

        return state.robot_mastery.get_robot_buff()

    @reducer_method
    def elapse(self, time: float, state: RobotSummonState):
        state = state.copy()

        state.cooldown.elapse(time)
        lapse_count = state.periodic.elapse(time)

        return state, [self.event_provider.elapsed(time)] + [
            self.event_provider.dealt(
                self.tick_damage,
                self.tick_hit,
                modifier=state.robot_mastery.get_robot_modifier(),
            )
            for _ in range(lapse_count)
        ]

    @reducer_method
    def use(self, _: None, state: RobotSummonState):
        return self.use_tick_emitting_trait(state)

    @view_method
    def validity(self, state: RobotSummonState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: RobotSummonState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            duration=self._get_duration(state),
        )

    def _get_duration(self, state: RobotSummonState) -> float:
        return self.duration * state.robot_mastery.get_summon_multiplier()

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_tick_damage_hit(self, state: RobotSummonState) -> tuple[float, float]:
        return self.tick_damage, self.tick_hit


class HommingMissileState(ReducerState):
    bomber_time: Duration
    buster_call: Keydown
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class HommingMissile(
    SkillComponent, StartIntervalWithoutDamageTrait, CooldownValidityTrait
):
    binds: dict[str, str] = {
        "bomber_time": ".봄버 타임.duration",
        "buster_call": ".메탈아머 전탄발사.keydown",
    }
    name: str
    cooldown: float
    delay: float

    tick_interval: float
    tick_damage: float
    tick_hit: float
    duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.tick_interval, time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: HommingMissileState):
        return self.use_tick_emitting_without_damage_trait(state)

    @reducer_method
    def elapse(
        self,
        time: float,
        state: HommingMissileState,
    ):
        state = state.copy()

        state.cooldown.elapse(time)
        lapse_count = state.periodic.elapse(time)

        return state, [self.event_provider.elapsed(time)] + [
            self.event_provider.dealt(
                self.tick_damage, self.get_homming_missile_hit(state)
            )
            for _ in range(lapse_count)
        ]

    def get_homming_missile_hit(self, state: HommingMissileState) -> int:
        hit = int(self.tick_hit)
        if state.bomber_time.enabled():
            hit += 5

        if state.buster_call.is_running():
            hit += 7

        if (
            not state.buster_call.is_running()
            and state.buster_call.time_elapsed_after_latest_action < 2_000
        ):
            hit = 0

        return hit

    @view_method
    def validity(self, state: HommingMissileState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: HommingMissileState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            duration=self._get_duration(state),
        )

    def _get_duration(self, state: HommingMissileState) -> float:
        return self.duration

    def _get_tick_damage_hit(self, state: HommingMissileState) -> tuple[float, float]:
        return self.tick_damage, self.tick_hit


class MultipleOptionState(ReducerState):
    cycle: Cycle
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics
    robot_mastery: RobotMastery


class MultipleOptionComponent(SkillComponent, CooldownValidityTrait):
    name: str
    cooldown: float
    delay: float

    tick_interval: float
    duration: float

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
            "periodic": Periodic(interval=self.tick_interval, time_left=0),
            "cycle": Cycle(tick=0, period=self.missile_count + self.gatling_count),
        }

    def get_damage_event(
        self,
        state: MultipleOptionState,
    ) -> Event:
        if state.cycle.get_tick() < self.missile_count:
            return self.event_provider.dealt(
                self.missile_damage,
                self.missile_hit,
                modifier=state.robot_mastery.get_robot_modifier(),
            )

        return self.event_provider.dealt(
            self.gatling_damage,
            self.gatling_hit,
            modifier=state.robot_mastery.get_robot_modifier(),
        )

    @reducer_method
    def elapse(self, time: float, state: MultipleOptionState):
        state = state.copy()

        state.cooldown.elapse(time)
        dealing_events = []

        for _ in state.periodic.resolving(time):
            dealing_events.append(self.get_damage_event(state))
            state.cycle.step()

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: MultipleOptionState):
        state = state.copy()

        if not state.cooldown.available:
            return state, self.event_provider.rejected()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown)
        )
        state.periodic.set_time_left(self.duration)
        state.cycle.clear()

        return state, [
            self.event_provider.delayed(self.delay),
        ]

    @view_method
    def buff(self, state: MultipleOptionState):
        if not state.periodic.enabled():
            return None

        return state.robot_mastery.get_robot_buff()

    @view_method
    def validity(self, state: MultipleOptionState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: MultipleOptionState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            duration=self._get_duration(state),
        )

    def _get_duration(self, state: MultipleOptionState) -> float:
        return self.duration


class DynamicIntervalPeriodic(Entity):
    interval_counter: float = 0.0
    interval: float
    time_left: float = 0.0
    count: int = 0
    count_interval_penalty: float
    max_count: int

    def set_time_left(self, time: float, count: int):
        self.time_left = time
        self.interval_counter = self.interval
        self.count = count

    def enabled(self):
        return self.time_left > 0

    def resolving(self, time: float):
        maximum_elapsed = max(0, int(self.time_left // self.interval))

        self.time_left -= time
        self.interval_counter -= time
        elapse_count = 0

        while self.interval_counter <= 0 and elapse_count < maximum_elapsed:
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
    cooldown: float
    delay: float
    duration: float

    tick_interval: float

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
                interval=self.tick_interval,
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
        state = state.copy()
        state.cooldown.elapse(time)

        dealing_events = []

        for intercepter_count in state.periodic.resolving(time):
            dealing_events.append(
                self.event_provider.dealt(
                    self.damage_per_intercepter,
                    self.hit_per_intercepter * intercepter_count,
                    modifier=state.robot_mastery.get_robot_modifier(),
                )
            )

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: MecaCarrierState):
        state = state.copy()

        if not state.cooldown.available:
            return state, self.event_provider.rejected()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown)
        )

        state.periodic.set_time_left(self.duration, self.start_intercepter)

        return state, [
            self.event_provider.delayed(self.delay),
        ]

    @view_method
    def buff(self, state: MecaCarrierState):
        if not state.periodic.enabled():
            return None

        return state.robot_mastery.get_robot_buff()

    @view_method
    def validity(self, state: MecaCarrierState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: MecaCarrierState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            stack=state.periodic.count if state.periodic.time_left > 0 else 0,
            duration=self._get_duration(state),
        )

    def _get_duration(self, state: MecaCarrierState) -> float:
        return self.duration
