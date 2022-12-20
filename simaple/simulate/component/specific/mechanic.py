from typing import Optional

from simaple.core import Stat
from simaple.simulate.base import Event, State
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.keydown_skill import KeydownState
from simaple.simulate.component.skill import (
    CooldownState,
    DurationState,
    IntervalState,
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


class RobotMasteryState(State):
    summon_increment: float
    robot_damage_increment: float
    robot_buff_damage_multiplier: float

    def get_robot_modifier(self) -> Stat:
        return Stat(final_damage_multiplier=self.robot_damage_increment)

    def get_robot_buff(self) -> Stat:
        return Stat(damage_multiplier=self.robot_buff_damage_multiplier)


class RobotMastery(Component):
    summon_increment: float
    robot_damage_increment: float
    robot_buff_damage_multiplier: float

    def get_default_state(self):
        return {
            "robot_mastery": RobotMasteryState(
                summon_increment=self.summon_increment,
                robot_damage_increment=self.robot_damage_increment,
                robot_buff_damage_multiplier=self.robot_buff_damage_multiplier,
            )
        }


class RobotSetupBuff(SkillComponent, DurableTrait, CooldownValidityTrait):
    stat: Stat
    cooldown: float = 0.0
    delay: float
    duration: float
    binds: dict[str, str] = {"robot_mastery": ".로봇 마스터리.robot_mastery"}

    def get_default_state(self):
        return {
            "cooldown_state": CooldownState(time_left=0),
            "duration_state": DurationState(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        duration_state: DurationState,
        dynamics: Dynamics,
        robot_mastery: RobotMasteryState,
    ):
        states, event = self.use_durable_trait(
            cooldown_state,
            duration_state,
            dynamics,
            (1 + robot_mastery.summon_increment / 100),
        )
        return (*states, robot_mastery), event

    @reducer_method
    def elapse(
        self, time: float, cooldown_state: CooldownState, duration_state: DurationState
    ):
        return self.elapse_durable_trait(time, cooldown_state, duration_state)

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_cooldown_trait(cooldown_state)

    @view_method
    def buff(
        self, duration_state: DurationState, robot_mastery: RobotMasteryState
    ) -> Optional[Stat]:
        if duration_state.enabled():
            return self.stat + robot_mastery.get_robot_buff()

        return None

    @view_method
    def running(self, duration_state: DurationState) -> Running:
        return Running(name=self.name, time_left=duration_state.time_left)

    def _get_duration(self) -> float:
        return self.duration


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
            "cooldown_state": CooldownState(time_left=0),
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
        }

    @view_method
    def buff(self, interval_state: IntervalState, robot_mastery: RobotMasteryState):
        if not interval_state.enabled():
            return None

        return robot_mastery.get_robot_buff()

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        robot_mastery: RobotMasteryState,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        cooldown_state.elapse(time)
        lapse_count = interval_state.elapse(time)

        return (cooldown_state, interval_state, robot_mastery), [
            self.event_provider.elapsed(time)
        ] + [
            self.event_provider.dealt(
                self.tick_damage,
                self.tick_hit,
                modifier=robot_mastery.get_robot_modifier(),
            )
            for _ in range(lapse_count)
        ]

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        dynamics: Dynamics,
        robot_mastery: RobotMastery,
    ):
        states, event = self.use_tick_emitting_trait(
            cooldown_state,
            interval_state,
            dynamics,
            (1 + robot_mastery.summon_increment / 100),
        )
        return (*states, robot_mastery), event

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_cooldown_trait(cooldown_state)

    @view_method
    def running(self, interval_state: IntervalState) -> Running:
        return Running(name=self.name, time_left=interval_state.interval_time_left)

    def _get_duration(self) -> float:
        return self.duration

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_tick_damage_hit(self) -> tuple[float, float]:
        return self.tick_damage, self.tick_hit


class HommingMissile(
    SkillComponent, StartIntervalWithoutDamageTrait, CooldownValidityTrait
):
    binds: dict[str, str] = {
        "bomber_time": ".봄버 타임.duration_state",
        "buster_call": ".메탈아머 전탄발사.keydown_state",
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
            "cooldown_state": CooldownState(time_left=0),
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        dynamics: Dynamics,
    ):
        return self.use_tick_emitting_without_damage_trait(
            cooldown_state, interval_state, dynamics
        )

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        bomber_time: DurationState,
        buster_call: KeydownState,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        cooldown_state.elapse(time)
        lapse_count = interval_state.elapse(time)

        return (cooldown_state, interval_state, bomber_time, buster_call), [
            self.event_provider.elapsed(time)
        ] + [
            self.event_provider.dealt(
                self.tick_damage, self.get_homming_missile_hit(bomber_time, buster_call)
            )
            for _ in range(lapse_count)
        ]

    def get_homming_missile_hit(
        self, bomber_time: DurationState, buster_call: KeydownState
    ) -> int:
        hit = int(self.tick_hit)
        if bomber_time.enabled():
            hit += 5

        if buster_call.is_running():
            hit += 7

        if (
            not buster_call.is_running()
            and buster_call.time_elapsed_after_latest_action < 2_000
        ):
            hit = 0

        return hit

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_cooldown_trait(cooldown_state)

    @view_method
    def running(self, interval_state: IntervalState) -> Running:
        return Running(name=self.name, time_left=interval_state.interval_time_left)

    def _get_duration(self) -> float:
        return self.duration

    def _get_tick_damage_hit(self) -> tuple[float, float]:
        return self.tick_damage, self.tick_hit


class PeriodicState(State):
    tick: int
    period: int

    def step(self):
        self.tick += 1
        self.tick = self.tick % self.period

    def get_tick(self) -> int:
        return self.tick

    def clear(self):
        self.tick = 0


class MultipleOptionComponent(SkillComponent, CooldownValidityTrait):
    name: str
    cooldown: float = 0.0
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
            "cooldown_state": CooldownState(time_left=0),
            "interval_state": IntervalState(interval=self.tick_interval, time_left=0),
            "period": PeriodicState(
                tick=0, period=self.missile_count + self.gatling_count
            ),
        }

    def get_damage_event(
        self, period: PeriodicState, robot_mastery: RobotMasteryState
    ) -> Event:
        if period.get_tick() < self.missile_count:
            return self.event_provider.dealt(
                self.missile_damage,
                self.missile_hit,
                modifier=robot_mastery.get_robot_modifier(),
            )

        return self.event_provider.dealt(
            self.gatling_damage,
            self.gatling_hit,
            modifier=robot_mastery.get_robot_modifier(),
        )

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        robot_mastery: RobotMasteryState,
        period: PeriodicState,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        cooldown_state.elapse(time)
        dealing_events = []

        for _ in interval_state.resolving(time):
            dealing_events.append(self.get_damage_event(period, robot_mastery))
            period.step()

        return (cooldown_state, interval_state, robot_mastery, period), [
            self.event_provider.elapsed(time)
        ] + dealing_events

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        period: PeriodicState,
        dynamics: Dynamics,
    ):
        cooldown_state, interval_state, period = (
            cooldown_state.copy(),
            interval_state.copy(),
            period.copy(),
        )

        if not cooldown_state.available:
            return (cooldown_state, interval_state), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))
        interval_state.set_time_left(self.duration)
        period.clear()

        return (cooldown_state, interval_state, period, dynamics), [
            self.event_provider.delayed(self.delay),
        ]

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return self.validity_in_cooldown_trait(cooldown_state)

    @view_method
    def running(self, interval_state: IntervalState) -> Running:
        return Running(name=self.name, time_left=interval_state.interval_time_left)


class DynamicIntervalState(State):
    interval_counter: float = 0.0
    interval: float
    interval_time_left: float = 0.0
    count: int = 0
    count_interval_penalty: float
    max_count: int

    def set_time_left(self, time: float, count: int):
        self.interval_time_left = time
        self.interval_counter = self.interval
        self.count = count

    def enabled(self):
        return self.interval_time_left > 0

    def resolving(self, time: float):
        maximum_elapsed = max(0, int(self.interval_time_left // self.interval))

        self.interval_time_left -= time
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
        self.interval_time_left = 0


class MecaCarrier(SkillComponent, CooldownValidityTrait):
    name: str
    cooldown: float = 0.0
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
            "cooldown_state": CooldownState(time_left=0),
            "interval_state": DynamicIntervalState(
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
        cooldown_state: CooldownState,
        interval_state: DynamicIntervalState,
        robot_mastery: RobotMasteryState,
    ):
        cooldown_state, interval_state = cooldown_state.copy(), interval_state.copy()

        cooldown_state.elapse(time)

        dealing_events = []

        for intercepter_count in interval_state.resolving(time):
            dealing_events.append(
                self.event_provider.dealt(
                    self.damage_per_intercepter,
                    self.hit_per_intercepter * intercepter_count,
                    modifier=robot_mastery.get_robot_modifier(),
                )
            )

        return (cooldown_state, interval_state, robot_mastery), [
            self.event_provider.elapsed(time)
        ] + dealing_events

    @reducer_method
    def use(
        self,
        _: None,
        cooldown_state: CooldownState,
        interval_state: DynamicIntervalState,
        dynamics: Dynamics,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        if not cooldown_state.available:
            return (cooldown_state, interval_state), self.event_provider.rejected()

        cooldown_state.set_time_left(dynamics.stat.calculate_cooldown(self.cooldown))

        interval_state.set_time_left(self.duration, self.start_intercepter)

        return (cooldown_state, interval_state, dynamics), [
            self.event_provider.delayed(self.delay),
        ]

    @view_method
    def validity(self, cooldown_state):
        return self.validity_in_cooldown_trait(cooldown_state)

    @view_method
    def running(self, interval_state: DynamicIntervalState) -> Running:
        return Running(name=self.name, time_left=interval_state.interval_time_left)
