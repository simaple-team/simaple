from typing import List, Optional

from pydantic import BaseModel, Field

from simaple.core import Stat
from simaple.gear.arcane_symbol import ArcaneSymbol
from simaple.gear.authentic_symbol import AuthenticSymbol
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType


class GearSlot(BaseModel):
    name: str
    enabled_gear_types: List[GearType]
    gear: Optional[Gear]

    def is_equipped(self):
        return self.gear is not None

    def is_equippable(self, gear):
        return gear.type in self.enabled_gear_types

    def equip(self, gear):
        if not self.is_equippable(gear):
            raise ValueError

        self.gear = gear

    def get_gear(self) -> Gear:
        if self.gear is None:
            raise ValueError

        return self.gear


def get_default_empty_slots():
    return [
        GearSlot(name="cap", enabled_gear_types=[GearType.cap]),
        GearSlot(name="face_accessory", enabled_gear_types=[GearType.face_accessory]),
        GearSlot(name="eye_accessory", enabled_gear_types=[GearType.eye_accessory]),
        GearSlot(name="earrings", enabled_gear_types=[GearType.earrings]),
        GearSlot(name="coat", enabled_gear_types=[GearType.coat, GearType.longcoat]),
        GearSlot(name="pants", enabled_gear_types=[GearType.pants]),
        GearSlot(name="shoes", enabled_gear_types=[GearType.shoes]),
        GearSlot(name="glove", enabled_gear_types=[GearType.glove]),
        GearSlot(name="cape", enabled_gear_types=[GearType.cape]),
        GearSlot(name="ring1", enabled_gear_types=[GearType.ring]),
        GearSlot(name="ring2", enabled_gear_types=[GearType.ring]),
        GearSlot(name="ring3", enabled_gear_types=[GearType.ring]),
        GearSlot(name="ring4", enabled_gear_types=[GearType.ring]),
        GearSlot(name="pendant1", enabled_gear_types=[GearType.pendant]),
        GearSlot(name="pendant2", enabled_gear_types=[GearType.pendant]),
        GearSlot(name="belt", enabled_gear_types=[GearType.belt]),
        GearSlot(name="medal", enabled_gear_types=[GearType.medal]),
        GearSlot(name="shoulder_pad", enabled_gear_types=[GearType.shoulder_pad]),
        GearSlot(name="pocket", enabled_gear_types=[GearType.pocket]),
        GearSlot(name="badge", enabled_gear_types=[GearType.badge]),
        GearSlot(name="android", enabled_gear_types=[GearType.android]),
        GearSlot(name="machine_heart", enabled_gear_types=[GearType.machine_heart]),
        GearSlot(
            name="subweapon",
            enabled_gear_types=[
                gear_type for gear_type in GearType if GearType.is_sub_weapon(gear_type)
            ],
        ),
        GearSlot(name="emblem", enabled_gear_types=[GearType.emblem]),
        GearSlot(
            name="weapon",
            enabled_gear_types=[
                gear_type for gear_type in GearType if GearType.is_weapon(gear_type)
            ],
        ),
    ]


class Gearset(BaseModel):
    arcane_symbols: List[ArcaneSymbol] = Field(default_factory=list)
    authentic_symbols: List[AuthenticSymbol] = Field(default_factory=list)
    pet_equip: Stat = Field(default_factory=Stat)
    pet_set_option: Stat = Field(default_factory=Stat)
    cash_item_stat: Stat = Field(default_factory=Stat)

    gear_slots: List[GearSlot] = Field(default_factory=get_default_empty_slots)

    title: Stat = Field(default_factory=Stat)

    def set_arcane_symbols(self, arcane_symbols: List[ArcaneSymbol]):
        self.arcane_symbols = list(arcane_symbols)

    def set_authentic_symbols(self, authentic_symbols: List[AuthenticSymbol]):
        self.authentic_symbols = list(authentic_symbols)

    def get_arcane_symbol_stat(self) -> Stat:
        return sum([v.get_stat() for v in self.arcane_symbols], Stat())

    def get_authentic_symbol_stat(self) -> Stat:
        return sum([v.get_stat() for v in self.authentic_symbols], Stat())

    def get_gear_slot_stat(self) -> Stat:
        stat = Stat()
        for slot in self.gear_slots:
            if slot.gear is not None:
                stat += slot.gear.sum_stat()

        return stat

    def get_total_stat(self) -> Stat:
        stat = Stat()
        stat += self.get_gear_slot_stat()
        stat += self.get_arcane_symbol_stat()
        stat += self.get_authentic_symbol_stat()
        stat += self.pet_equip
        stat += self.pet_set_option
        stat += self.cash_item_stat
        stat += self.title

        return stat

    def set_pet_equip_stat(self, stat: Stat):
        self.pet_equip = stat

    def set_pet_set_option(self, stat: Stat):
        self.pet_set_option = stat

    def set_cash_item_stat(self, stat: Stat):
        self.cash_item_stat = stat

    def set_title_stat(self, stat: Stat):
        self.title = stat

    def is_all_slot_equipped(self):
        for slot in self.gear_slots:
            if not slot.is_equipped():
                return False

        return True

    def _get_eqiuppable_slots(self, gear) -> List[GearSlot]:
        return [
            slot for slot in self.gear_slots if gear.type in slot.enabled_gear_types
        ]

    def get_slot(self, slot_name: str) -> GearSlot:
        for slot in self.gear_slots:
            if slot.name == slot_name:
                return slot

        raise KeyError

    def equip(self, gear: Gear, slot_name: str) -> None:
        self.get_slot(slot_name).equip(gear)
