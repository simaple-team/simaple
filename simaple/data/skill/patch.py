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

        previous_modifier = Stat.model_validate(output.get("modifier", {}))
        scale = self.improvements.get(output["name"], 0)
        new_modifier = previous_modifier + Stat(
            final_damage_multiplier=improvement_scale * scale
        )
        if scale > 40:
            new_modifier += Stat(ignored_defence=20)

        output["modifier"] = new_modifier.short_dict()

        return output


class HexaSkillImprovementPatch(Patch):
    improvements: dict[str, int] = pydantic.Field(default_factory=dict)

    def _compute_final_damage_multiplier(self, level: int) -> Stat:
        if level == 0:
            return Stat()
        if 0 < level < 10:
            return Stat(final_damage_multiplier=10 + level)
        if 10 <= level < 20:
            return Stat(final_damage_multiplier=15 + level)
        if 20 <= level < 30:
            return Stat(final_damage_multiplier=20 + level)
        if level == 30:
            return Stat(final_damage_multiplier=60)

        raise ValueError(f"Invalid level: {level}")

    def apply(self, raw: dict) -> dict:
        output = copy.deepcopy(raw)
        previous_modifier = Stat.model_validate(output.get("modifier", {}))

        level = self.improvements.get(output["name"], 0)
        new_modifier = previous_modifier + self._compute_final_damage_multiplier(level)
        output["modifier"] = new_modifier.short_dict()

        return output
