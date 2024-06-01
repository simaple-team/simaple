import copy
from typing import Any

import pydantic

from simaple.core import Stat
from simaple.data.passive_hyper_skill import get_every_hyper_skills
from simaple.data.passive_hyper_skill.spec import PassiveHyperskillInterface
from simaple.spec.patch import Patch


def _get_representative_skill_name(raw: dict[str, Any]) -> str:
    """
    Returns representative skill name for skill.
    `Representative skill name` is the skill name that is used to
    determine which patch may adopted for that skill.
    """
    if "representative_name" in raw:
        assert isinstance(raw["representative_name"], str)
        return raw["representative_name"]

    assert isinstance(raw["name"], str)
    return raw["name"]


class PassiveHyperskillPatch(Patch):
    hyper_skills: list[PassiveHyperskillInterface]

    def apply(self, raw: dict) -> dict:
        output = raw
        skill_name = _get_representative_skill_name(raw)
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
    """
    Update 4-th skill damage increased by `v_improvement` value.

    5차 코어에 의한 4차 스킬의 최종 데미지 증가분을 반영합니다.
    """

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
        level = self.improvements.get(_get_representative_skill_name(raw), 0)
        new_modifier = previous_modifier + Stat(
            final_damage_multiplier=improvement_scale * level
        )
        if level > 40:
            new_modifier += Stat(ignored_defence=20)

        output["modifier"] = new_modifier.short_dict()

        return output


class HexaSkillImprovementPatch(Patch):
    """
    Update 5-th skill damage increased by `vi_improvement` value.

    6차 코어에 의한 5차 스킬의 최종 데미지 증가분을 반영합니다.
    """

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

        level = self.improvements.get(_get_representative_skill_name(raw), 0)
        new_modifier = previous_modifier + self._compute_final_damage_multiplier(level)
        output["modifier"] = new_modifier.short_dict()

        return output
