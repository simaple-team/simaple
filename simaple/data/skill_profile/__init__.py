from pathlib import Path
from typing import cast

import pydantic

from simaple.core import JobType
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository


class SkillProfile(
    pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta(kind="SkillProfile")
):
    """
    SkillProfile
    A pre-assigned information to create specific job's components easier
    """

    v_skill_names: list[str]
    v_improvement_names: list[str]
    hexa_improvement_names: list[str]
    component_groups: list[str]
    hexa_skill_names: list[str] = pydantic.Field(default=[])
    hexa_mastery: dict[str, str] = pydantic.Field(default={})

    def get_filled_v_skill(self, level: int = 30) -> dict[str, int]:
        return {k: level for k in self.v_skill_names}

    def get_skill_levels(
        self, v_level: int, hexa_level: int, hexa_mastery_level: int
    ) -> dict[str, int]:
        skill_levels = {}
        skill_levels.update(self.get_filled_v_skill(v_level))
        skill_levels.update(self.get_filled_hexa_skill(hexa_level))
        skill_levels.update(
            {skill: hexa_mastery_level for skill in self.hexa_mastery.values()}
        )
        return skill_levels

    def get_filled_hexa_skill(self, level: int) -> dict[str, int]:
        """
        TODO: refactor skill level injection strategy
        """
        return {k: level for k in self.hexa_skill_names}

    def get_filled_v_improvements(self, level: int = 60) -> dict[str, int]:
        return {k: level for k in self.v_improvement_names}

    def get_filled_hexa_improvements(self, level: int = 1) -> dict[str, int]:
        return {k: level for k in self.hexa_improvement_names}

    def get_groups(self) -> list[str]:
        return self.component_groups

    def get_skill_replacements(self) -> dict[str, str]:
        return self.hexa_mastery


def get_skill_profile(jobtype: JobType) -> SkillProfile:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    return cast(
        SkillProfile,
        loader.load(
            query={"group": jobtype.value, "kind": "SkillProfile"},
        ),
    )
