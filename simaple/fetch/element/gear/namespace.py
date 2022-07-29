import enum
from typing import Dict, Union

from simaple.core.base import StatProps


class PropertyNamespace(enum.Enum):
    all_stat_multiplier = "all_stat_multiplier"
    misc = "misc"
    all_stat = "all_stat"


Namespace = Union[StatProps, PropertyNamespace]


class StatType(enum.Enum):
    sum = "sum"
    base = "base"
    bonus = "bonus"
    increment = "increment"
    potential = "potential"
    additional_potential = "additional_potential"
    name = "name"
    soulweapon = "soulweapon"
    starforce = "starforce"
    image = "image"
    surprise = "surprise"


def korean_names() -> Dict[str, Namespace]:
    return {
        "STR": StatProps.STR,
        "DEX": StatProps.DEX,
        "LUK": StatProps.LUK,
        "INT": StatProps.INT,
        "STR%": StatProps.STR_multiplier,
        "DEX%": StatProps.DEX_multiplier,
        "LUK%": StatProps.LUK_multiplier,
        "INT%": StatProps.INT_multiplier,
        "STRF": StatProps.STR_static,
        "DEXF": StatProps.DEX_static,
        "LUKF": StatProps.LUK_static,
        "INTF": StatProps.INT_static,
        "MaxHP": StatProps.MHP,
        "MaxMP": StatProps.MMP,
        "공격력": StatProps.attack_power,
        "마력": StatProps.magic_attack,
        "보스몬스터공격시데미지": StatProps.boss_damage_multiplier,
        "보스몬스터공격시데미지%": StatProps.boss_damage_multiplier,
        "올스탯%": PropertyNamespace.all_stat_multiplier,
        "올스탯": PropertyNamespace.all_stat,
        "데미지": StatProps.damage_multiplier,
        "데미지%": StatProps.damage_multiplier,
        "몬스터방어력무시": StatProps.ignored_defence,
        "몬스터방어율무시": StatProps.ignored_defence,
        "크리티컬확률": StatProps.critical_rate,
        "크리티컬데미지": StatProps.critical_damage,
        "몬스터방어력무시%": StatProps.ignored_defence,
        "몬스터방어율무시%": StatProps.ignored_defence,
        "크리티컬확률%": StatProps.critical_rate,
        "크리티컬데미지%": StatProps.critical_damage,
    }
