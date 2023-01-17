from pathlib import Path
from typing import Optional

from simaple.character.passive_skill import PassiveSkill
from simaple.core import JobType, Stat
from simaple.data.passive.patch import SkillLevelPatch
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch, Patch
from simaple.spec.repository import DirectorySpecRepository


def get_patches(
    combat_orders_level: int,
    passive_skill_level: int,
    character_level: int,
    weapon_pure_attack_power: Optional[int] = None,
) -> list[Patch]:
    return [
        SkillLevelPatch(
            combat_orders_level=combat_orders_level,
            passive_skill_level=passive_skill_level,
        ),
        EvalPatch(
            injected_values={
                "character_level": character_level,
                "weapon_pure_attack_power": weapon_pure_attack_power,
            }
        ),
    ]


def get_passive_stat(
    jobtype: JobType,
    combat_orders_level: int,
    passive_skill_level: int,
    character_level: int,
    weapon_pure_attack_power: Optional[int] = None,
) -> Stat:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    patches = get_patches(
        combat_orders_level,
        passive_skill_level,
        character_level,
        weapon_pure_attack_power=weapon_pure_attack_power,
    )
    passive_skills = loader.load_all(
        query={"group": jobtype.value, "kind": "PassiveSkill"}, patches=patches
    )

    return sum(
        [passive_skill.stat for passive_skill in passive_skills],
        Stat(),
    )
