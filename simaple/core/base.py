from __future__ import annotations

import enum

from pydantic import BaseModel


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

    @classmethod
    def all_stat(cls, v):
        return Stat(STR=v, LUK=v, INT=v, DEX=v)

    @classmethod
    def all_stat_multiplier(cls, v):
        return Stat(
            STR_multiplier=v, LUK_multiplier=v, INT_multiplier=v, DEX_multiplier=v
        )

    def __add__(self, arg: Stat):
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
            final_damage_multiplier=self.final_damage_multiplier
            + arg.final_damage_multiplier
            + 0.01 * self.final_damage_multiplier * arg.final_damage_multiplier,
            ignored_defence=100
            - 0.01 * ((100 - self.ignored_defence) * (100 - arg.ignored_defence)),
        )

    def __iadd__(self, arg):
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

        self.final_damage_multiplier += (
            arg.final_damage_multiplier
            + 0.01 * self.final_damage_multiplier * arg.final_damage_multiplier
        )
        self.ignored_defence = 100 - 0.01 * (
            (100 - self.ignored_defence) * (100 - arg.ignored_defence)
        )

        return self

    def get(self, prop: StatProps):
        return getattr(self, prop)
