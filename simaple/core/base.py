from __future__ import annotations

import enum
from typing import Union

from pydantic import BaseModel, Extra, Field


class BaseStatType(enum.Enum):
    STR = "STR"
    LUK = "LUK"
    INT = "INT"
    DEX = "DEX"


class AttackType(enum.Enum):
    attack_power = "attack_power"
    magic_attack = "magic_attack"


class StatProps(enum.Enum):
    STR = "STR"
    LUK = "LUK"
    INT = "INT"
    DEX = "DEX"

    STR_multiplier = "STR_multiplier"
    LUK_multiplier = "LUK_multiplier"
    INT_multiplier = "INT_multiplier"
    DEX_multiplier = "DEX_multiplier"

    STR_static = "STR_static"
    LUK_static = "LUK_static"
    INT_static = "INT_static"
    DEX_static = "DEX_static"

    attack_power = "attack_power"
    magic_attack = "magic_attack"
    attack_power_multiplier = "attack_power_multiplier"
    magic_attack_multiplier = "magic_attack_multiplier"

    critical_rate = "critical_rate"
    critical_damage = "critical_damage"

    boss_damage_multiplier = "boss_damage_multiplier"
    damage_multiplier = "damage_multiplier"
    final_damage_multiplier = "final_damage_multiplier"

    ignored_defence = "ignored_defence"

    MHP = "MHP"
    MMP = "MMP"

    MHP_multiplier = "MHP_multiplier"
    MMP_multiplier = "MMP_multiplier"


class Stat(BaseModel):
    STR: float = 0.0
    LUK: float = 0.0
    INT: float = 0.0
    DEX: float = 0.0

    STR_multiplier: float = 0.0
    LUK_multiplier: float = 0.0
    INT_multiplier: float = 0.0
    DEX_multiplier: float = 0.0

    STR_static: float = 0.0
    LUK_static: float = 0.0
    INT_static: float = 0.0
    DEX_static: float = 0.0

    attack_power: float = 0.0
    magic_attack: float = 0.0
    attack_power_multiplier: float = 0.0
    magic_attack_multiplier: float = 0.0

    critical_rate: float = 0.0
    critical_damage: float = 0.0

    boss_damage_multiplier: float = 0.0
    damage_multiplier: float = 0.0
    final_damage_multiplier: float = 0.0

    ignored_defence: float = 0.0

    MHP: float = 0.0
    MMP: float = 0.0

    MHP_multiplier: float = 0.0
    MMP_multiplier: float = 0.0

    elemental_resistance: float = 0.0

    class Config:
        extra = Extra.forbid

    @classmethod
    def all_stat(cls, v) -> Stat:
        return Stat(STR=v, LUK=v, INT=v, DEX=v)

    @classmethod
    def all_stat_multiplier(cls, v) -> Stat:
        return Stat(
            STR_multiplier=v, LUK_multiplier=v, INT_multiplier=v, DEX_multiplier=v
        )

    def __add__(self, arg: Stat) -> Stat:
        return Stat(
            STR=self.STR + arg.STR,
            LUK=self.LUK + arg.LUK,
            INT=self.INT + arg.INT,
            DEX=self.DEX + arg.DEX,
            STR_multiplier=self.STR_multiplier + arg.STR_multiplier,
            LUK_multiplier=self.LUK_multiplier + arg.LUK_multiplier,
            INT_multiplier=self.INT_multiplier + arg.INT_multiplier,
            DEX_multiplier=self.DEX_multiplier + arg.DEX_multiplier,
            STR_static=self.STR_static + arg.STR_static,
            LUK_static=self.LUK_static + arg.LUK_static,
            INT_static=self.INT_static + arg.INT_static,
            DEX_static=self.DEX_static + arg.DEX_static,
            attack_power=self.attack_power + arg.attack_power,
            magic_attack=self.magic_attack + arg.magic_attack,
            attack_power_multiplier=self.attack_power_multiplier
            + arg.attack_power_multiplier,
            magic_attack_multiplier=self.magic_attack_multiplier
            + arg.magic_attack_multiplier,
            critical_rate=self.critical_rate + arg.critical_rate,
            critical_damage=self.critical_damage + arg.critical_damage,
            boss_damage_multiplier=self.boss_damage_multiplier
            + arg.boss_damage_multiplier,
            damage_multiplier=self.damage_multiplier + arg.damage_multiplier,
            MHP=self.MHP + arg.MHP,
            MMP=self.MMP + arg.MMP,
            MHP_multiplier=self.MHP_multiplier + arg.MHP_multiplier,
            MMP_multiplier=self.MMP_multiplier + arg.MMP_multiplier,
            final_damage_multiplier=self.final_damage_multiplier
            + arg.final_damage_multiplier
            + 0.01 * self.final_damage_multiplier * arg.final_damage_multiplier,
            ignored_defence=100
            - 0.01 * ((100 - self.ignored_defence) * (100 - arg.ignored_defence)),
            elemental_resistance=self.elemental_resistance + arg.elemental_resistance,
        )

    def __iadd__(self, arg: Stat):
        self.STR += arg.STR
        self.LUK += arg.LUK
        self.INT += arg.INT
        self.DEX += arg.DEX

        self.STR_multiplier += arg.STR_multiplier
        self.LUK_multiplier += arg.LUK_multiplier
        self.INT_multiplier += arg.INT_multiplier
        self.DEX_multiplier += arg.DEX_multiplier

        self.STR_static += arg.STR_static
        self.LUK_static += arg.LUK_static
        self.INT_static += arg.INT_static
        self.DEX_static += arg.DEX_static

        self.attack_power += arg.attack_power
        self.magic_attack += arg.magic_attack

        self.attack_power_multiplier += arg.attack_power_multiplier
        self.magic_attack_multiplier += arg.magic_attack_multiplier

        self.critical_rate += arg.critical_rate
        self.critical_damage += arg.critical_damage

        self.boss_damage_multiplier += arg.boss_damage_multiplier
        self.damage_multiplier += arg.damage_multiplier

        self.MHP += arg.MHP
        self.MMP += arg.MMP

        self.MHP_multiplier += arg.MHP_multiplier
        self.MMP_multiplier += arg.MMP_multiplier

        self.final_damage_multiplier += (
            arg.final_damage_multiplier
            + 0.01 * self.final_damage_multiplier * arg.final_damage_multiplier
        )
        self.ignored_defence = 100 - 0.01 * (
            (100 - self.ignored_defence) * (100 - arg.ignored_defence)
        )
        self.elemental_resistance += arg.elemental_resistance

        return self

    def stack(self, stack: int) -> Stat:
        """
        StackableBuffSkill을 위한 메소드로, armor_ignore 및 final_damage_multiplier를 단순 곱셈한 값을 반환합니다.
        """
        return Stat(
            STR=self.STR * stack,
            LUK=self.LUK * stack,
            INT=self.INT * stack,
            DEX=self.DEX * stack,
            STR_multiplier=self.STR_multiplier * stack,
            LUK_multiplier=self.LUK_multiplier * stack,
            INT_multiplier=self.INT_multiplier * stack,
            DEX_multiplier=self.DEX_multiplier * stack,
            STR_static=self.STR_static * stack,
            LUK_static=self.LUK_static * stack,
            INT_static=self.INT_static * stack,
            DEX_static=self.DEX_static * stack,
            attack_power=self.attack_power * stack,
            magic_attack=self.magic_attack * stack,
            attack_power_multiplier=self.attack_power_multiplier * stack,
            magic_attack_multiplier=self.magic_attack_multiplier * stack,
            critical_rate=self.critical_rate * stack,
            critical_damage=self.critical_damage * stack,
            boss_damage_multiplier=self.boss_damage_multiplier * stack,
            damage_multiplier=self.damage_multiplier * stack,
            MHP=self.MHP * stack,
            MMP=self.MMP * stack,
            MHP_multiplier=self.MHP_multiplier * stack,
            MMP_multiplier=self.MMP_multiplier * stack,
            final_damage_multiplier=self.final_damage_multiplier * stack,
            ignored_defence=self.ignored_defence * stack,
            elemental_resistance=self.elemental_resistance * stack,
        )

    def get(self, prop: StatProps):
        return getattr(self, prop.value)

    def get_base_stat_coefficient(self, base_stat_type: BaseStatType) -> float:
        if base_stat_type == BaseStatType.STR:
            return self.STR * (self.STR_multiplier * 0.01 + 1) + self.STR_static
        if base_stat_type == BaseStatType.DEX:
            return self.DEX * (self.DEX_multiplier * 0.01 + 1) + self.DEX_static
        if base_stat_type == BaseStatType.INT:
            return self.INT * (self.INT_multiplier * 0.01 + 1) + self.INT_static
        if base_stat_type == BaseStatType.LUK:
            return self.LUK * (self.LUK_multiplier * 0.01 + 1) + self.LUK_static

        raise ValueError

    def get_attack_coefficient(self, attack_type: AttackType) -> float:
        if attack_type == AttackType.attack_power:
            return self.attack_power * (1 + 0.01 * self.attack_power_multiplier)
        if attack_type == AttackType.magic_attack:
            return self.magic_attack * (1 + 0.01 * self.magic_attack_multiplier)

        raise ValueError

    def show(self) -> str:
        output = f"""
        ===================================
        Basis Stats

        STR: {self.get_base_stat_coefficient(BaseStatType.STR):8.2f} | Basis {self.STR:7.1f} | {self.STR_multiplier:5.1f} % | static {self.STR_static:7.1f} |
        DEX: {self.get_base_stat_coefficient(BaseStatType.DEX):8.2f} | Basis {self.DEX:7.1f} | {self.DEX_multiplier:5.1f} % | static {self.DEX_static:7.1f} |
        INT: {self.get_base_stat_coefficient(BaseStatType.INT):8.2f} | Basis {self.INT:7.1f} | {self.INT_multiplier:5.1f} % | static {self.INT_static:7.1f} |
        LUK: {self.get_base_stat_coefficient(BaseStatType.LUK):8.2f} | Basis {self.LUK:7.1f} | {self.LUK_multiplier:5.1f} % | static {self.LUK_static:7.1f} |
        
        MaxHP: Basis {self.MHP:10.2f} | {self.MHP_multiplier:5.1f} % 
        MaxMP: Basis {self.MMP:10.2f} | {self.MMP_multiplier:5.1f} % 

        ATT: {self.attack_power:6.1f} | {self.attack_power_multiplier:5.1f} % |
        MAT: {self.magic_attack:6.1f} | {self.magic_attack_multiplier:5.1f} % |

        ===================================

        critical_rate          : {self.critical_rate:7.2f}
        critical_damage        : {self.critical_damage:7.2f}

        boss_damage_multiplier : {self.boss_damage_multiplier:7.2f}
        damage_multiplier      : {self.damage_multiplier:7.2f}
        final_damage_multiplier: {self.final_damage_multiplier:7.2f}

        ignored_defence        : {self.ignored_defence:7.2f}
        elemental_resistance   : { self.elemental_resistance:7.2f}
        """
        return output

    def short_dict(self) -> dict[str, float]:
        long_dict = self.dict()
        return {k: v for k, v in long_dict.items() if v != 0}


class ActionStat(BaseModel):
    cooltime_reduce: float = 0.0
    summon_duration: float = 0.0
    buff_duration: float = 0.0
    cooltime_reduce_rate: float = 0.0

    class Config:
        extra = Extra.forbid

    def __add__(self, arg: ActionStat) -> ActionStat:
        return ActionStat(
            cooltime_reduce=self.cooltime_reduce + arg.cooltime_reduce,
            summon_duration=self.summon_duration + arg.summon_duration,
            buff_duration=self.buff_duration + arg.buff_duration,
            cooltime_reduce_rate=self.cooltime_reduce_rate + arg.cooltime_reduce_rate,
        )

    def __iadd__(self, arg: ActionStat) -> ActionStat:
        self.cooltime_reduce += arg.cooltime_reduce
        self.summon_duration += arg.summon_duration
        self.buff_duration += arg.buff_duration
        self.cooltime_reduce_rate += arg.cooltime_reduce_rate
        return self

    def calculate_cooldown(self, original_cooldown):
        # TODO - need to apply correct logic
        return (
            original_cooldown * (1 - self.cooltime_reduce_rate * 0.01)
            - self.cooltime_reduce
        )

    def calculate_buff_duration(self, original_duration):
        return original_duration * (1 + 0.01 * self.buff_duration)


class LevelStat(BaseModel):
    STR: float = 0.0
    LUK: float = 0.0
    INT: float = 0.0
    DEX: float = 0.0

    attack_power: float = 0.0
    magic_attack: float = 0.0

    class Config:
        extra = Extra.forbid

    def get_stat(self, level: int) -> Stat:
        multiplier = level // 10
        return Stat(
            STR=self.STR * multiplier,
            LUK=self.LUK * multiplier,
            INT=self.INT * multiplier,
            DEX=self.DEX * multiplier,
            attack_power=self.attack_power * multiplier,
            magic_attack=self.magic_attack * multiplier,
        )

    def __add__(self, arg: LevelStat):
        return LevelStat(
            STR=self.STR + arg.STR,
            LUK=self.LUK + arg.LUK,
            INT=self.INT + arg.INT,
            DEX=self.DEX + arg.DEX,
            attack_power=self.attack_power + arg.attack_power,
            magic_attack=self.magic_attack + arg.magic_attack,
        )


AnyStat = Union[Stat, ActionStat, LevelStat]


class ExtendedStat(BaseModel):
    stat: Stat = Field(default_factory=Stat)
    action_stat: ActionStat = Field(default_factory=ActionStat)
    level_stat: LevelStat = Field(default_factory=LevelStat)

    def __add__(self, arg: ExtendedStat) -> ExtendedStat:
        return ExtendedStat(
            stat=self.stat + arg.stat,
            action_stat=self.action_stat + arg.action_stat,
            level_stat=self.level_stat + arg.level_stat,
        )

    def compute_by_level(self, level) -> Stat:
        return self.stat + self.level_stat.get_stat(level)
