import copy
import math  # pylint: disable=W0611
from typing import Union

import pydantic

from simaple.core import Stat
from simaple.job.description import GeneralJobArgument
from simaple.spec.patch import DFSTraversePatch, Patch


class SkillLevelPatch(DFSTraversePatch):
    job_argument: GeneralJobArgument
    skill_level_representation: str = "skill_level"
    default_skill_levels: dict[str, int] = pydantic.Field(default_factory=dict)

    def patch_value(self, value, origin: dict):
        return self.translate(value, origin)

    def patch_dict(self, k, v, origin: dict):
        return {self.translate(k, origin): self.translate(v, origin)}

    def translate(
        self, maybe_representation: Union[int, str, float], origin: dict
    ) -> Union[int, str, float]:
        if not isinstance(maybe_representation, str):
            return maybe_representation

        output = maybe_representation.replace(
            self.skill_level_representation, str(self.get_skill_level(origin))
        )

        return output

    def get_skill_level(self, origin: dict):
        if origin.get("name") and self.default_skill_levels.get(origin["name"]):
            skill_level = self.default_skill_levels.get(origin["name"])
        else:
            skill_level = origin.get("default_skill_level", 0)
        if origin.get("passive_skill_enabled", False):
            skill_level += self.job_argument.passive_skill_level
        if origin.get("combat_orders_enabled", False):
            skill_level += self.job_argument.combat_orders_level

        return skill_level


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
        new_modifier = previous_modifier + Stat(
            final_damage_multiplier=improvement_scale
            * self.improvements.get(output["name"], 0)
        )
        output["modifier"] = new_modifier.short_dict()

        return output
