import copy
from typing import Any, TypedDict, TypeVar, Union, cast

import pydantic

from simaple.core import Stat
from simaple.data.jobs.definitions import PassiveHyperskillInterface
from simaple.data.jobs.definitions.skill_improvement import SkillImprovement
from simaple.spec.patch import DFSTraversePatch, Patch


def _get_referencing_skill_name(raw: dict[str, Any], payload: dict | None) -> str:
    if payload is not None:
        return cast(str, payload["level_reference_name"])

    assert isinstance(raw["name"], str)
    return raw["name"]


class PassiveHyperskillPatch(Patch):
    hyper_skills: list[PassiveHyperskillInterface]

    def apply(self, raw: dict[str, Any], payload: dict | None = None) -> dict[str, Any]:
        output = raw

        skill_name = _get_referencing_skill_name(raw, payload)

        for hyper_skill in self.hyper_skills:
            if hyper_skill.get_target_name() == skill_name:
                output = hyper_skill.modify(output)

        return output


class VSkillImprovementPatch(Patch):
    """
    Update 4-th skill damage increased by `v_improvement` value.

    5차 코어에 의한 4차 스킬의 최종 데미지 증가분을 반영합니다.
    """

    improvements: dict[str, int] = pydantic.Field(default_factory=dict)

    def apply(self, raw: dict[str, Any], payload: dict | None = None) -> dict[str, Any]:
        output = copy.deepcopy(raw)
        try:
            improvement_scale = output.pop("v_improvement")
        except KeyError as e:
            raise KeyError(
                "VSkillImprovementPatch assigned but no `v_improvement`."
            ) from e

        previous_modifier = Stat.model_validate(output.get("modifier", {}))

        skill_name = _get_referencing_skill_name(raw, payload)

        level = self.improvements.get(skill_name, 0)

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

    def apply(self, raw: dict[str, Any], payload: dict | None = None) -> dict[str, Any]:
        output = copy.deepcopy(raw)
        previous_modifier = Stat.model_validate(output.get("modifier", {}))

        skill_name = _get_referencing_skill_name(raw, payload)

        level = self.improvements.get(skill_name, 0)
        new_modifier = previous_modifier + self._compute_final_damage_multiplier(level)
        output["modifier"] = new_modifier.short_dict()

        return output


class SkillImprovementPatch(Patch):
    improvements: list[SkillImprovement]

    def apply(self, raw: dict[str, Any], payload: dict | None = None) -> dict[str, Any]:
        output = raw

        for improvement in self.improvements:
            output = improvement.modify(output)

        if output == raw:
            raise ValueError(
                f"At least one improvement should be applied if skill improvement patch defined"
            )

        return output


class SkillLevelPatch(DFSTraversePatch):
    combat_orders_level: int
    passive_skill_level: int
    skill_level_representation: str = "skill_level"
    default_skill_levels: dict[str, int] = {}

    def patch_value(self, value, origin: dict):
        return self.translate(value, origin)

    def patch_dict(self, k, v, origin: dict):
        return {k: self.translate(v, origin)}

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
            skill_level: int = self.default_skill_levels[origin["name"]]
        else:
            skill_level = origin.get("default_skill_level", 0)
        if origin.get("passive_skill_enabled", False):
            skill_level += self.passive_skill_level
        if origin.get("combat_orders_enabled", False):
            skill_level += self.combat_orders_level

        return skill_level
