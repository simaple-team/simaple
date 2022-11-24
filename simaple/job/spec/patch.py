import math  # pylint: disable=W0611
from typing import Union

from simaple.job.description import GeneralJobArgument
from simaple.spec.patch import DFSTraversePatch


class SkillLevelPatch(DFSTraversePatch):
    job_argument: GeneralJobArgument
    skill_level_representation: str = "skill_level"
    default_skill_levels: dict[str, int]

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
