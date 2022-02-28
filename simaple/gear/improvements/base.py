from simaple.core.base import Stat
from pydantic import BaseModel
from simaple.gear.gear_type import GearType
from simaple.gear.gear import Gear
from typing import Literal, List

import enum


class GearImprovement(BaseModel):
    type: str
    def calculate_improvement(self, gear: Gear) -> Stat:
        ...


class Scroll(BaseModel):
    type: Literal['Scroll']
    stat: Stat
    name: str
    gear_types: List[GearType]

