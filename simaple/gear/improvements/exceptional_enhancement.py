from typing import Literal, Optional

from simaple.core import Stat
from simaple.gear.gear import GearMeta
from simaple.gear.improvements.base import GearImprovement


class ExceptionalEnhancement(GearImprovement):
    type: Literal["ExceptionalEnhancement"] = "ExceptionalEnhancement"
    stat: Stat

    def calculate_improvement(
        self, meta: GearMeta, ref_stat: Optional[Stat] = None
    ) -> Stat:
        return self.stat.copy()
