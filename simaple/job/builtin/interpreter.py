from pathlib import Path

from simaple.job.spec.patch import SkillLevelPatch
from simaple.job.static_property import StaticProperty
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
    group: str, combat_orders_level: int, passive_skill_level: int, character_level: int
):
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    patches = get_patches(combat_orders_level, passive_skill_level, character_level)
    return loader.load_all(
        query={"group": group, "kind": "PassiveSkill"}, patches=patches
    )


def get_default_active_skills(
    group: str, combat_orders_level: int, passive_skill_level: int, character_level: int
):
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    patches = get_patches(combat_orders_level, passive_skill_level, character_level)

    return loader.load_all(
        query={"group": group, "kind": "DefaultActiveSkill"}, patches=patches
    )


def get_static_propery(
    group: str, combat_orders_level: int, passive_skill_level: int, character_level: int
):
    return StaticProperty(
        passive_skillset=get_passive_skills(
            group, combat_orders_level, passive_skill_level, character_level
        ),
        default_active_skillset=get_default_active_skills(
            group, combat_orders_level, passive_skill_level, character_level
        ),
    )
