import copy

import pydantic

from simaple.core import Stat
from simaple.spec.patch import Patch


class VSkillImprovementPatch(Patch):
    improvements: dict[str, int] = pydantic.Field(default_factory=dict)

    def apply(self, raw: dict) -> dict:
        output = copy.deepcopy(raw)
        try:
            improvement_scale = output.pop("v_improvement")
        except KeyError as e:
            raise KeyError(
                "VSkillImprovementPatch assigned but no `v_improvement`."
            ) from e

        previous_modifier = Stat.parse_obj(output.get("modifier", {}))
        scale = self.improvements.get(output["name"], 0)
        new_modifier = previous_modifier + Stat(
            final_damage_multiplier=improvement_scale * scale
        )
        if scale > 40:
            new_modifier += Stat(ignored_defence=20)

        output["modifier"] = new_modifier.short_dict()

        return output
