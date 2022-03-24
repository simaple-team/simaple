from typing import List, Literal, Optional

from pydantic import BaseModel

from simaple.core import Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType


class Scroll(BaseModel):
    type: Literal["Scroll"] = "Scroll"
    stat: Stat
    name: str
    gear_types: Optional[List[GearType]]

    def calculate_improvement(self, gear: Gear) -> Stat:
        if not self.is_gear_acceptable(gear):
            raise TypeError("Given gear type is not available to use this scroll")

        return self.stat.copy()

    def is_gear_acceptable(self, gear: Gear) -> bool:
        return self.gear_types is None or gear.type in self.gear_types
