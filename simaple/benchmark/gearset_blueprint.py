from typing import List, Tuple

from pydantic import BaseModel

from simaple.core import Stat
from simaple.gear.arcane_symbol import ArcaneSymbol
from simaple.gear.authentic_symbol import AuthenticSymbol
from simaple.gear.blueprint import PracticalGearBlueprint
from simaple.gear.gear_repository import GearRepository
from simaple.gear.gearset import Gearset
from simaple.gear.potential import PotentialTier


class UserGearsetBlueprint(BaseModel):
    arcane_symbols: List[ArcaneSymbol]
    authentic_symbols: List[AuthenticSymbol]
    pet_equip: Stat
    pet_set: Stat
    cash: Stat
    weapon_potential_tiers: Tuple[
        List[PotentialTier], List[PotentialTier], List[PotentialTier],
    ]

    cap: PracticalGearBlueprint
    coat: PracticalGearBlueprint
    pants: PracticalGearBlueprint
    shoes: PracticalGearBlueprint
    glove: PracticalGearBlueprint
    cape: PracticalGearBlueprint
    shoulder_pad: PracticalGearBlueprint
    face_accessory: PracticalGearBlueprint
    eye_accessory: PracticalGearBlueprint
    earrings: PracticalGearBlueprint
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

    machine_heart: PracticalGearBlueprint

    title: Stat

    def build(self, gear_repository: GearRepository) -> Gearset:
        gearset = Gearset()

        gearset.equip(self.cap.build(gear_repository=gear_repository), "cap")
        gearset.equip(self.coat.build(gear_repository=gear_repository), "coat")
        gearset.equip(self.pants.build(gear_repository=gear_repository), "pants")
        gearset.equip(self.shoes.build(gear_repository=gear_repository), "shoes")
        gearset.equip(self.glove.build(gear_repository=gear_repository), "glove")
        gearset.equip(self.cape.build(gear_repository=gear_repository), "cape")
        gearset.equip(
            self.shoulder_pad.build(gear_repository=gear_repository), "shoulder_pad"
        )
        gearset.equip(
            self.face_accessory.build(gear_repository=gear_repository), "face_accessory"
        )
        gearset.equip(
            self.eye_accessory.build(gear_repository=gear_repository), "eye_accessory"
        )
        gearset.equip(self.earrings.build(gear_repository=gear_repository), "earrings")
        gearset.equip(self.belt.build(gear_repository=gear_repository), "belt")

        gearset.equip(self.ring1.build(gear_repository=gear_repository), "ring1")
        gearset.equip(self.ring2.build(gear_repository=gear_repository), "ring2")
        gearset.equip(self.ring3.build(gear_repository=gear_repository), "ring3")
        gearset.equip(self.ring4.build(gear_repository=gear_repository), "ring4")

        gearset.equip(self.pendant1.build(gear_repository=gear_repository), "pendant1")
        gearset.equip(self.pendant2.build(gear_repository=gear_repository), "pendant2")

        gearset.equip(self.pocket.build(gear_repository=gear_repository), "pocket")
        gearset.equip(self.badge.build(gear_repository=gear_repository), "badge")
        gearset.equip(self.medal.build(gear_repository=gear_repository), "medal")

        gearset.equip(self.weapon.build(gear_repository=gear_repository), "weapon")
        gearset.equip(
            self.subweapon.build(gear_repository=gear_repository), "subweapon"
        )
        gearset.equip(self.emblem.build(gear_repository=gear_repository), "emblem")
        gearset.equip(
            self.machine_heart.build(gear_repository=gear_repository), "machine_heart"
        )

        gearset.set_title_stat(self.title)

        gearset.set_arcane_symbols(self.arcane_symbols)
        gearset.set_authentic_symbols(self.authentic_symbols)

        gearset.set_pet_equip_stat(self.pet_equip)
        gearset.set_pet_set_option(self.pet_set)
        gearset.set_cash_item_stat(self.cash)

        return gearset
