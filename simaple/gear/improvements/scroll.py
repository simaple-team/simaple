from simaple.core.base import Stat
from pydantic import BaseModel, conint
from simaple.gear.gear_type import GearType
from simaple.gear.gear import Gear
from simaple.gear.improvements.base import GearImprovement
from typing import Literal, List

import enum
import math


class Scroll(BaseModel):
    type: Literal['Scroll']
    stat: Stat
    name: str
    gear_types: List[GearType]

    def calculate_improvement(self, gear: Gear) -> Stat:
        if not self.is_gear_acceptable(gear):
            raise TypeError("Given gear type is not available to use this scroll")
            
        return self.stat.copy()

    def is_gear_acceptable(self, gear: Gear) -> bool:
        return gear.type in self.gear_types
