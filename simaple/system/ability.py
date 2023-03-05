import enum

import pydantic

from simaple.core.base import ActionStat, ExtendedStat, Stat


class AbilityType(enum.Enum):
    attack_power = "attack_power"
    magic_attack = "magic_attack"
    boss_damage_multiplier = "boss_damage_multiplier"
    abnormal_status_damage_multiplier = "abnormal_status_damage_multiplier"
    cooldown_reset_chance = "cooldown_reset_chance"
    buff_duration = "buff_duration"
    critical_rate = "critical_rate"
    passive_skill_level = "passive_skill_level"


class AbilityLine(pydantic.BaseModel):
    type: AbilityType
    value: int


def get_ability_stat_from_line(line: AbilityLine) -> ExtendedStat:
    if line.type == AbilityType.attack_power:
        return ExtendedStat(stat=Stat(attack_power=line.value))
    if line.type == AbilityType.magic_attack:
        return ExtendedStat(stat=Stat(magic_attack=line.value))
    if line.type == AbilityType.boss_damage_multiplier:
        return ExtendedStat(stat=Stat(boss_damage_multiplier=line.value))
    if line.type == AbilityType.abnormal_status_damage_multiplier:
        return ExtendedStat(stat=Stat(boss_damage_multiplier=line.value))
    if line.type == AbilityType.cooldown_reset_chance:
        return ExtendedStat()  # Not implemented yet
    if line.type == AbilityType.buff_duration:
        return ExtendedStat(action_stat=ActionStat(buff_duration=line.value))
    if line.type == AbilityType.critical_rate:
        return ExtendedStat(stat=Stat(critical_rate=line.value))
    if line.type == AbilityType.passive_skill_level:
        return ExtendedStat()
    raise ValueError("Invelid ability type")


def get_ability_stat(lines: list[AbilityLine]) -> ExtendedStat:
    return sum((get_ability_stat_from_line(line) for line in lines), ExtendedStat())
