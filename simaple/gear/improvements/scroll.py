from typing import Literal, Optional

from pydantic import BaseModel

from simaple.core import Stat
from simaple.gear.gear import GearMeta
from simaple.gear.gear_type import GearType


class Scroll(BaseModel):
    type: Literal["Scroll"] = "Scroll"
    stat: Stat
    name: str
    gear_types: list[GearType] = []

    def calculate_improvement(self, meta: GearMeta, _: Optional[Stat] = None) -> Stat:
        if not self.is_gear_acceptable(meta):
            raise TypeError("Given gear type is not available to use this scroll")

        return self.stat.model_copy()

    def is_gear_acceptable(self, meta: GearMeta) -> bool:
        if len(self.gear_types) == 0:
            return True

        return meta.type in self.gear_types
