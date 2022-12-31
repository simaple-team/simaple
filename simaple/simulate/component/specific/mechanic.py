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
from simaple.simulate.component.skill import Cooldown, Lasting, Periodic, SkillComponent
from simaple.simulate.component.trait.impl import (
    BuffTrait,
    CooldownValidityTrait,
    KeydownSkillTrait,
    PeriodicWithSimpleDamageTrait,
    UsePeriodicDamageTrait,
)
from simaple.simulate.component.util import is_keydown_ended
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
    lasting: Lasting
    dynamics: Dynamics


class RobotSetupBuff(SkillComponent, BuffTrait, CooldownValidityTrait):
    stat: Stat
    cooldown_duration: float
    delay: float
    lasting_duration: float
    binds: dict[str, str] = {"robot_mastery": ".로봇 마스터리.robot_mastery"}

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "lasting": Lasting(time_left=0),
        }

    @reducer_method
    def use(
        self,
        _: None,
        state: RobotSetupBuffState,
    ):
        return self.use_buff_trait(state)

    @reducer_method
    def elapse(self, time: float, state: RobotSetupBuffState):
        return self.elapse_buff_trait(time, state)

    @view_method
    def validity(self, state: RobotSetupBuffState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def buff(self, state: RobotSetupBuffState) -> Optional[Stat]:
        if state.lasting.enabled():
            return self.stat + state.robot_mastery.get_robot_buff()

        return None

    @view_method
    def running(self, state: RobotSetupBuffState) -> Running:
        return Running(
            name=self.name,
            time_left=state.lasting.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: RobotSetupBuffState) -> float:
        return self.lasting_duration * state.robot_mastery.get_summon_multiplier()


class RobotSummonState(ReducerState):
    robot_mastery: RobotMastery
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class RobotSummonSkill(
    SkillComponent, PeriodicWithSimpleDamageTrait, CooldownValidityTrait
):
    binds: dict[str, str] = {"robot_mastery": ".로봇 마스터리.robot_mastery"}
    name: str
    damage: float
    hit: float
    cooldown_duration: float
    delay: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @view_method
    def buff(self, state: RobotSummonState):
        if not state.periodic.enabled():
            return None

        return state.robot_mastery.get_robot_buff()

    @reducer_method
    def elapse(self, time: float, state: RobotSummonState):
        state = state.deepcopy()

        state.cooldown.elapse(time)
        lapse_count = state.periodic.elapse(time)

        return state, [self.event_provider.elapsed(time)] + [
            self.event_provider.dealt(
                self.periodic_damage,
                self.periodic_hit,
                modifier=state.robot_mastery.get_robot_modifier(),
            )
            for _ in range(lapse_count)
        ]

    @reducer_method
    def use(self, _: None, state: RobotSummonState):
        return self.use_periodic_damage_trait(state)

    @view_method
    def validity(self, state: RobotSummonState):
        return self.validity_in_cooldown_trait(state)

    @view_method
    def running(self, state: RobotSummonState) -> Running:
        return Running(
            name=self.name,
            time_left=state.periodic.time_left,
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: RobotSummonState) -> float:
        return self.lasting_duration * state.robot_mastery.get_summon_multiplier()

    def _get_simple_damage_hit(self) -> tuple[float, float]:
        return self.damage, self.hit

    def _get_periodic_damage_hit(self, state: RobotSummonState) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit


class HommingMissileState(ReducerState):
    bomber_time: Lasting
    full_barrage_keydown: Keydown
    full_barrage_penalty_lasting: Lasting
    cooldown: Cooldown
    periodic: Periodic
    dynamics: Dynamics


class HommingMissile(SkillComponent, UsePeriodicDamageTrait, CooldownValidityTrait):
    binds: dict[str, str] = {
        "bomber_time": ".봄버 타임.lasting",
        "full_barrage_keydown": ".메탈아머 전탄발사.keydown",
        "full_barrage_penalty_lasting": ".메탈아머 전탄발사.penalty_lasting",
    }
    name: str
    cooldown_duration: float
    delay: float

    periodic_interval: float
    periodic_damage: float
    periodic_hit: float
    lasting_duration: float

    def get_default_state(self):
        return {
            "cooldown": Cooldown(time_left=0),
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
        }

    @reducer_method
    def use(self, _: None, state: HommingMissileState):
        return self.use_periodic_damage_trait(state)

    @reducer_method
    def elapse(
        self,
        time: float,
        state: HommingMissileState,
    ):
        state = state.deepcopy()

        state.cooldown.elapse(time)
        lapse_count = state.periodic.elapse(time)

        return state, [self.event_provider.elapsed(time)] + [
            self.event_provider.dealt(
                self.periodic_damage, self.get_homming_missile_hit(state)
            )
            for _ in range(lapse_count)
        ]

    def get_homming_missile_hit(self, state: HommingMissileState) -> int:
        hit = int(self.periodic_hit)
        if state.bomber_time.enabled():
            hit += 5

        if state.full_barrage_keydown.running:
            hit += 7

        if state.full_barrage_penalty_lasting.enabled():
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
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: HommingMissileState) -> float:
        return self.lasting_duration

    def _get_periodic_damage_hit(
        self, state: HommingMissileState
    ) -> tuple[float, float]:
        return self.periodic_damage, self.periodic_hit


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
            "periodic": Periodic(interval=self.periodic_interval, time_left=0),
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
        state = state.deepcopy()

        state.cooldown.elapse(time)
        dealing_events = []

        for _ in state.periodic.resolving(time):
            dealing_events.append(self.get_damage_event(state))
            state.cycle.step()

        return state, [self.event_provider.elapsed(time)] + dealing_events

    @reducer_method
    def use(self, _: None, state: MultipleOptionState):
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, self.event_provider.rejected()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
        )
        state.periodic.set_time_left(self.lasting_duration)
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
        state = state.deepcopy()

        if not state.cooldown.available:
            return state, self.event_provider.rejected()

        state.cooldown.set_time_left(
            state.dynamics.stat.calculate_cooldown(self.cooldown_duration)
        )

        state.periodic.set_time_left(self.lasting_duration, self.start_intercepter)

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
            lasting_duration=self._get_lasting_duration(state),
        )

    def _get_lasting_duration(self, state: MecaCarrierState) -> float:
        return self.lasting_duration
