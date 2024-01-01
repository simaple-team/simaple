import copy

import pydantic

from simaple.core import Stat
from simaple.spec.patch import Patch

from simaple.data.passive_hyper_skill.spec import PassiveHyperskillInterface
from simaple.data.passive_hyper_skill import get_every_hyper_skills
from simaple.spec.patch import Patch


class PassiveHyperskillPatch(Patch):
    hyper_skills: list[PassiveHyperskillInterface]

    def apply(self, raw: dict) -> dict:
        output = raw
        skill_name = raw["name"]
        for hyper_skill in self.hyper_skills:
            if hyper_skill.get_target_name() == skill_name:
                output = hyper_skill.modify(output)

        return output



def get_hyper_skill_patch(
    group: str,
    skill_names: list[str] | None = None,
    count=5,
):
    hyper_skills = get_every_hyper_skills(group)

    if skill_names is None:
        hyper_skills = hyper_skills[:count]
    else:
        hyper_skills = [sk for sk in hyper_skills if sk.get_name() in skill_names]

    return PassiveHyperskillPatch(hyper_skills=hyper_skills)


class VSkillImprovementPatch(Patch):
    improvements: dict[str, int] = pydantic.Field(default_factory=dict)

    def _get_improvement_level(self, raw: dict) -> str:
        target_name = raw["name"]
        if "v_improvement_name" in raw:
            return raw["v_improvement"]

        return self.improvements.get(target_name, 0)

    def apply(self, raw: dict) -> dict:
        output = copy.deepcopy(raw)
        try:
            improvement_scale = output.pop("v_improvement")
        except KeyError as e:
            raise KeyError(
                "VSkillImprovementPatch assigned but no `v_improvement`."
            ) from e

        previous_modifier = Stat.model_validate(output.get("modifier", {}))
        level = self._get_improvement_level(raw)
        new_modifier = previous_modifier + Stat(
            final_damage_multiplier=improvement_scale * level
        )
        if level > 40:
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
