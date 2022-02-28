from simaple.gear.gear_type import GearType
from pydantic import BaseModel
from simaple.core.base import Stat
from typing import List
import enum
import json
import os


class Gear(BaseModel):
    id: int
    stat: Stat
    name: str
    type: GearType
    req_level: int
    scroll_chance_left: int
    boss_reward: bool
    superior_eqp: bool

    def is_weapon(self) -> bool:
        return GearType.is_weapon(self.type)

    def is_left_weapon(self) -> bool:
        return GearType.is_left_weapon(self.type)

    def is_sub_weapon(self) -> bool:
        return GearType.is_sub_weapon(self.type)

    def is_double_hand_weapon(self) -> bool:
        return GearType.is_double_hand_weapon(self.type)

    def is_armor(self) -> bool:
        return GearType.is_armor(self.type)

    def is_accessory(self) -> bool:
        return GearType.is_accessory(self.type)

    def is_mechanic_gear(self) -> bool:
        return GearType.is_mechanic_gear(self.type)

    def is_dragon_gear(self) -> bool:
        return GearType.is_dragon_gear(self.type)
