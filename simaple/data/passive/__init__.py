from pathlib import Path

from simaple.character.passive_skill import DefaultActiveSkill, PassiveSkill
from simaple.core import JobType, Stat
from simaple.data.passive.patch import SkillLevelPatch
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch, Patch
from simaple.spec.repository import DirectorySpecRepository


def get_patches(
    combat_orders_level: int, passive_skill_level: int, character_level: int
) -> list[Patch]:
    return [
        SkillLevelPatch(
            combat_orders_level=combat_orders_level,
            passive_skill_level=passive_skill_level,
        ),
        EvalPatch(
            injected_values={
                "character_level": character_level,
            }
        ),
    ]


def get_passive_skills(
    jobtype: JobType,
    combat_orders_level: int,
    passive_skill_level: int,
    character_level: int,
) -> list[PassiveSkill]:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    patches = get_patches(combat_orders_level, passive_skill_level, character_level)
    return loader.load_all(
        query={"group": jobtype.value, "kind": "PassiveSkill"}, patches=patches
    )


def get_default_active_skills(
    jobtype: JobType,
    combat_orders_level: int,
    passive_skill_level: int,
    character_level: int,
) -> list[DefaultActiveSkill]:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    patches = get_patches(combat_orders_level, passive_skill_level, character_level)

    return loader.load_all(
        query={"group": jobtype.value, "kind": "DefaultActiveSkill"}, patches=patches
    )


def get_passive_and_default_active_stat(
    jobtype: JobType,
    combat_orders_level: int,
    passive_skill_level: int,
    character_level: int,
) -> Stat:
    passive_skills = get_passive_skills(
        jobtype, combat_orders_level, passive_skill_level, character_level
    )

    default_active_skills = get_default_active_skills(
        jobtype, combat_orders_level, passive_skill_level, character_level
    )

    return sum(
        [
            passive_skill.stat
            for passive_skill in (passive_skills + default_active_skills)
        ],
        Stat(),
    )
