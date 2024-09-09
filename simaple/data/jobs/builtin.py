from pathlib import Path
from typing import Optional, cast

import pydantic

from simaple.core import JobType
from simaple.core.base import ExtendedStat
from simaple.core.damage import DamageLogic
from simaple.core.jobtype import JobType
from simaple.data.jobs.definitions import PassiveHyperskillInterface
from simaple.data.jobs.definitions.passive import PassiveSkill
from simaple.data.jobs.definitions.skill_profile import SkillProfile
from simaple.data.patch import SkillLevelPatch
from simaple.spec.loadable import (  # pylint:disable=unused-import; noqa: F401
    TaggedNamespacedABCMeta,
)
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch, Patch
from simaple.spec.repository import DirectorySpecRepository


def get_skill_profile(jobtype: JobType) -> SkillProfile:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    return cast(
        SkillProfile,
        loader.load(
            query={"group": jobtype.value, "kind": "SkillProfile"},
        ),
    )


def get_every_hyper_skills(group: str) -> list[PassiveHyperskillInterface]:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    return loader.load_all(
        query={"group": group, "kind": "PassiveHyperskill"},
    )


def get_damage_logic(jobtype: JobType, combat_orders_level: int) -> DamageLogic:
    repository = DirectorySpecRepository(str(Path(__file__).parent))
    loader = SpecBasedLoader(repository)
    patches = [
        SkillLevelPatch(
            combat_orders_level=combat_orders_level,
            passive_skill_level=0,
        ),
        EvalPatch(injected_values={}),
    ]
    return cast(
        DamageLogic,
        loader.load(
            query={"group": jobtype.value, "kind": "DamageLogic"},
            patches=patches,
        ),
    )


def _get_patches(
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


def get_passive(
    jobtype: JobType,
    combat_orders_level: int,
    passive_skill_level: int,
    character_level: int,
    weapon_pure_attack_power: Optional[int] = None,
) -> ExtendedStat:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    patches = _get_patches(
        combat_orders_level,
        passive_skill_level,
        character_level,
        weapon_pure_attack_power=weapon_pure_attack_power,
    )
    passive_skills: list[PassiveSkill] = loader.load_all(
        query={"group": jobtype.value, "kind": "PassiveSkill"}, patches=patches
    )

    return sum(
        [passive_skill.get_extended_stat() for passive_skill in passive_skills],
        ExtendedStat(),
    )
