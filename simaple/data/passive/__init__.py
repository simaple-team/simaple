from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from simaple.core import ActionStat, ExtendedStat, JobType, Stat
from simaple.data.passive.patch import SkillLevelPatch
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch, Patch
from simaple.spec.repository import DirectorySpecRepository


class PassiveSkill(BaseModel, metaclass=TaggedNamespacedABCMeta("PassiveSkill")):
    """
    Passive is no-state no-change property of user-class.
    """

    stat: Stat = Field(default_factory=Stat)
    action_stat: ActionStat = Field(default_factory=ActionStat)
    name: str

    def get_extended_stat(self) -> ExtendedStat:
        return ExtendedStat(stat=self.stat.copy(), action_stat=self.action_stat.copy())


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


def get_passive(
    jobtype: JobType,
    combat_orders_level: int,
    passive_skill_level: int,
    character_level: int,
    weapon_pure_attack_power: Optional[int] = None,
) -> ExtendedStat:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    patches = get_patches(
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
