


import enum
from simaple.core.base import Stat
from simaple.gear.potential import Potential
from pydantic import BaseModel, Extra, Field, validator


class PotentialType(enum.Enum):
    normal = "normal"
    additional = "additional"


class PotentialFieldName(enum.Enum):
    DEX_multiplier = "DEX_multiplier"
    STR_multiplier = "STR_multiplier"
    LUK_multiplier = "LUK_multiplier"
    INT_multiplier = "INT_multiplier"

    STR = "STR"
    DEX = "DEX"
    LUK = "LUK"
    INT = "INT"

    magic_attack = "magic_attack"
    attack_power = "attack_power"

    boss_damage_multiplier = "boss_damage_multiplier"
    all_stat_multiplier = "all_stat_multiplier"

    attack_power_multiplier = "attack_power_multiplier"
    magic_attack_multiplier = "magic_attack_multiplier"
    critical_damage = "critical_damage"

class PotentialField(BaseModel):
    name: PotentialFieldName
    value: int


class PotentialTemplate(BaseModel):
    options: list[PotentialField] = Field(default_factory=list)


def field_to_value(field: PotentialField) -> Stat:
    return Stat.parse_obj({
        field.name.value: field.value
    })

def template_to_potential(spec: PotentialTemplate) -> Potential:
    return Potential(options=[
        field_to_value(field) for field in spec.options
    ])
