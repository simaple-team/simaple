import enum
from typing import Union

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
