from pydantic import BaseModel
from typing import Optional, List, Tuple, Dict, Union
from simaple.core.base import Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType
from simaple.gear.blueprint import PracticalGearBlueprint
from simaple.gear.gear_repository import GearRepository

import yaml
import enum


class Slot(BaseModel):
    gear: Optional[Gear] = None
    gear_type: GearType

    def is_equipable(self, gear):
        return gear.type == self.gear_type

    def equip(self, gear: Gear):
        if not self.is_equipable(gear):
            raise ValueError

        self.gear = gear


class UserGearsetBlueprint(BaseModel):
    arcane_symbol_levels: List[int]
    authentic_symbol_levels: List[int]
    pet_equip: Stat
    pet_set: Stat
    cash: Stat
    weapon_stat: Tuple[int, int]

    head: PracticalGearBlueprint
    top: PracticalGearBlueprint
    bottom: PracticalGearBlueprint
    shoes: PracticalGearBlueprint
    glove: PracticalGearBlueprint
    cape: PracticalGearBlueprint
    shoulder: PracticalGearBlueprint
    face: PracticalGearBlueprint
    eye: PracticalGearBlueprint
    ear: PracticalGearBlueprint
    belt: PracticalGearBlueprint

    ring1: PracticalGearBlueprint
    ring2: PracticalGearBlueprint
    ring3: PracticalGearBlueprint
    ring4: PracticalGearBlueprint

    pendant1: PracticalGearBlueprint
    pendant2: PracticalGearBlueprint

    pocket: PracticalGearBlueprint
    badge: PracticalGearBlueprint
    medal: PracticalGearBlueprint

    weapon: PracticalGearBlueprint
    subweapon: PracticalGearBlueprint
    emblem: PracticalGearBlueprint

    heart: PracticalGearBlueprint
    
    title: Stat

    def build(self, gear_repository: GearRepository) -> Stat:
        output = Stat()
        
        output += self.head.build(gear_repository=gear_repository).sum_stat()
        output += self.top.build(gear_repository=gear_repository).sum_stat()
        output += self.bottom.build(gear_repository=gear_repository).sum_stat()
        output += self.shoes.build(gear_repository=gear_repository).sum_stat()
        output += self.glove.build(gear_repository=gear_repository).sum_stat()
        output += self.cape.build(gear_repository=gear_repository).sum_stat()
        output += self.shoulder.build(gear_repository=gear_repository).sum_stat()
        output += self.face.build(gear_repository=gear_repository).sum_stat()
        output += self.eye.build(gear_repository=gear_repository).sum_stat()
        output += self.ear.build(gear_repository=gear_repository).sum_stat()
        output += self.belt.build(gear_repository=gear_repository).sum_stat()

        output += self.ring1.build(gear_repository=gear_repository).sum_stat()
        output += self.ring2.build(gear_repository=gear_repository).sum_stat()
        output += self.ring3.build(gear_repository=gear_repository).sum_stat()
        output += self.ring4.build(gear_repository=gear_repository).sum_stat()

        output += self.pendant1.build(gear_repository=gear_repository).sum_stat()
        output += self.pendant2.build(gear_repository=gear_repository).sum_stat()

        output += self.pocket.build(gear_repository=gear_repository).sum_stat()
        output += self.badge.build(gear_repository=gear_repository).sum_stat()
        output += self.medal.build(gear_repository=gear_repository).sum_stat()

        output += self.weapon.build(gear_repository=gear_repository).sum_stat()
        output += self.subweapon.build(gear_repository=gear_repository).sum_stat()
        output += self.emblem.build(gear_repository=gear_repository).sum_stat()

        output += self.heart.build(gear_repository=gear_repository).sum_stat()
        output += self.title

        return output
