from typing import Optional

from simaple.core import Stat
from simaple.simulate.base import State
from simaple.simulate.component.base import Component, reducer_method, view_method
from simaple.simulate.component.skill import (
    CooldownState,
    DurationState,
    IntervalState,
    StackState,
    TickDamageConfiguratedAttackSkillComponent,
)
from simaple.simulate.component.view import Running, Validity
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


class RobotSetupBuff(Component):
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
    ):
        cooldown_state, duration_state = cooldown_state.copy(), duration_state.copy()

        if not cooldown_state.available:
            return (
                cooldown_state,
                duration_state,
                dynamics,
            ), self.event_provider.rejected()

        cooldown_state.set_time_left(self.cooldown)
        duration_state.set_time_left(self.duration)

        return (cooldown_state, duration_state, dynamics), self.event_provider.delayed(
            self.delay
        )

    @reducer_method
    def elapse(
        self, time: float, cooldown_state: CooldownState, duration_state: DurationState
    ):
        cooldown_state, duration_state = cooldown_state.copy(), duration_state.copy()

        cooldown_state.elapse(time)
        duration_state.elapse(time)

        return (cooldown_state, duration_state), [
            self.event_provider.elapsed(time),
        ]

    @view_method
    def validity(self, cooldown_state: CooldownState):
        return Validity(
            name=self.name,
            time_left=max(0, cooldown_state.time_left),
            valid=cooldown_state.available,
        )

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


class RobotSummonSkill(TickDamageConfiguratedAttackSkillComponent):
    binds: dict[str, str] = {"robot_mastery": ".로봇 마스터리.robot_mastery"}

    @view_method
    def buff(self, interval_state: IntervalState, robot_mastery: RobotMasteryState):
        if not interval_state.enabled():
            return None

        return robot_mastery.get_robot_buff()


class HommingMissile(TickDamageConfiguratedAttackSkillComponent):
    binds: dict[str, str] = {"bomber_time": ".봄버 타임.duration_state"}

    @reducer_method
    def elapse(
        self,
        time: float,
        cooldown_state: CooldownState,
        interval_state: IntervalState,
        bomber_time: DurationState,
    ):
        cooldown_state = cooldown_state.copy()
        interval_state = interval_state.copy()

        cooldown_state.elapse(time)
        lapse_count = interval_state.elapse(time)

        return (cooldown_state, interval_state, bomber_time), [
            self.event_provider.elapsed(time)
        ] + [
            self.event_provider.dealt(
                self.tick_damage, self.get_homming_missile_hit(bomber_time)
            )
            for _ in range(lapse_count)
        ]

    def get_homming_missile_hit(self, bomber_time: DurationState) -> int:
        hit = self.tick_hit
        if bomber_time.enabled():
            hit += 5

        return hit
