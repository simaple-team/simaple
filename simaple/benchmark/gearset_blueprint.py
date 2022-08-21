from typing import List, Tuple

from pydantic import Field

from simaple.benchmark.base import GearsetBlueprint
from simaple.core import Stat
from simaple.gear.arcane_symbol import ArcaneSymbol
from simaple.gear.authentic_symbol import AuthenticSymbol
from simaple.gear.blueprint import PracticalGearBlueprint
from simaple.gear.gear_repository import GearRepository
from simaple.gear.gearset import Gearset
from simaple.gear.potential import PotentialTier
from simaple.gear.slot_name import SlotName


# TODO: weapon potential optimizer (stand-alone)
class UserGearsetBlueprint(GearsetBlueprint):
    arcane_symbols: List[ArcaneSymbol] = Field(default_factory=list)
    authentic_symbols: List[AuthenticSymbol] = Field(default_factory=list)
    pet_equip: Stat
    pet_set: Stat
    cash: Stat
    weapon_potential_tiers: Tuple[
        List[PotentialTier],
        List[PotentialTier],
        List[PotentialTier],
    ]
    title: Stat

    gears: dict[SlotName, PracticalGearBlueprint]

    def build(self, gear_repository: GearRepository) -> Gearset:
        gearset = Gearset()

        for slot_name, blueprint in self.gears.items():
            gearset.equip(blueprint.build(gear_repository=gear_repository), slot_name)

        gearset.set_title_stat(self.title)

        gearset.set_arcane_symbols(self.arcane_symbols)
        gearset.set_authentic_symbols(self.authentic_symbols)

        gearset.set_pet_equip_stat(self.pet_equip)
        gearset.set_pet_set_option(self.pet_set)
        gearset.set_cash_item_stat(self.cash)

        return gearset
