from __future__ import annotations
from pydantic import BaseModel



class Ability(BaseModel):
    STR: float = 0.0
    LUK: float = 0.0
    INT: float = 0.0
    DEX: float = 0.0

    def __add__(self, arg: Ability):
        return Ability(
            STR = self.STR+arg.STR,
            LUK = self.LUK+arg.LUK,
            INT = self.INT+arg.INT,
            DEX = self.DEX+arg.DEX,
        )

class Stat(BaseModel):
    ability: Ability = Ability()
    ability_multiplier: Ability = Ability()
    ability_static: Ability = Ability()

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

    def __add__(self, arg: Stat):
        return Stat(
            ability=self.ability + arg.ability,
            ability_multiplier=self.ability_multiplier + arg.ability_multiplier,
            ability_static=self.ability_static + arg.ability_static,

            attack_power=self.attack_power + arg.attack_power,
            magic_attack=self.magic_attack + arg.magic_attack,

            attack_power_multiplier=self.attack_power_multiplier + arg.attack_power_multiplier,
            magic_attack_multiplier=self.magic_attack_multiplier + arg.magic_attack_multiplier,

            critical_rate=self.critical_rate + arg.critical_rate,
            critical_damage=self.critical_damage + arg.critical_damage,

            boss_damage_multiplier=self.boss_damage_multiplier + arg.boss_damage_multiplier,
            damage_multiplier=self.damage_multiplier + arg.damage_multiplier,
    
            final_damage_multiplier=self.final_damage_multiplier + arg.final_damage_multiplier + 0.01 * self.final_damage_multiplier * arg.final_damage_multiplier,
            ignored_defence=100 - 0.01 * ((100 - self.ignored_defence) * (100 - arg.ignored_defence)),
        )
