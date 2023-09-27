from typing import Literal, Optional

from simaple.core import Stat
from simaple.gear.gear import GearMeta
from simaple.gear.improvements.base import GearImprovement, InvalidImprovementException


class ExceptionalEnhancement(GearImprovement):
    type: Literal["ExceptionalEnhancement"] = "ExceptionalEnhancement"
    stat: Stat

    def calculate_improvement(
        self, meta: GearMeta, ref_stat: Optional[Stat] = None
    ) -> Stat:
        if not meta.exceptional_enhancement:
            raise InvalidImprovementException(
                "Given gear cannot improved by exceptional parts"
            )

        return self.stat.model_copy()
