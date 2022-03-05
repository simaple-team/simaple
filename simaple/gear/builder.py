from typing import List, Optional

from pydantic import BaseModel, Field

from simaple.core.base import Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository
from simaple.gear.improvements.bonus import Bonus
from simaple.gear.improvements.scroll import Scroll
from simaple.gear.improvements.spell_trace import SpellTrace
from simaple.gear.improvements.starforce import Starforce


class GearMetadata(BaseModel):
    gear_id: int
    spell_traces: List[SpellTrace] = Field(default_factory=list)
    scrolls: List[Scroll] = Field(default_factory=list)
    starforce: Starforce
    bonuses: List[Bonus] = Field(default_factory=list)


class PracticalGearMetadata(BaseModel):
    gear_id: int
    spell_trace: Optional[SpellTrace]
    scroll: Optional[Scroll]
    starforce: int
    bonus: Bonus


class GearBuilder:
    def __init__(self, gear_repository: GearRepository):
        self._gear_repository = gear_repository

    def build(self, gear_metadata: GearMetadata) -> Gear:
        gear = self._gear_repository.get_by_id(gear_metadata.gear_id)

        bonus_stat = sum(
            [bonus.calculate_improvement(gear) for bonus in gear_metadata.bonuses],
            Stat(),
        )
        # Apply spell trace and scroll.
        spell_trace_and_scoll_stat = sum(
            [
                spell_trace.calculate_improvement(gear)
                for spell_trace in gear_metadata.spell_traces
            ],
            Stat(),
        ) + sum(
            [scroll.calculate_improvement(gear) for scroll in gear_metadata.scrolls],
            Stat(),
        )

        gear.stat += spell_trace_and_scoll_stat

        # Apply Starforce
        gear.stat += gear_metadata.starforce.calculate_improvement(gear)

        # Apply bonus
        gear.stat += bonus_stat

        return gear
