import json
import os
import pathlib
from pathlib import Path
from typing import cast

import pydantic

from simaple.core import Stat
from simaple.core.damage import (
    DamageLogic,
    DEXBasedDamageLogic,
    INTBasedDamageLogic,
    LUKBasedDamageLogic,
    STRBasedDamageLogic,
)
from simaple.core.jobtype import JobType
from simaple.data.passive.patch import SkillLevelPatch
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.patch import EvalPatch, Patch
from simaple.spec.repository import DirectorySpecRepository


class DamageLogicConfiguration(
    pydantic.BaseModel,
    metaclass=TaggedNamespacedABCMeta(kind="DamageLogicConfiguration"),
):
    attack_range_constant: float
    mastery: float
    damage_logic_type: str


def get_damage_logic_from_config(conf: DamageLogicConfiguration) -> DamageLogic:
    if conf.damage_logic_type == "STR":
        return STRBasedDamageLogic(
            attack_range_constant=conf.attack_range_constant,
            mastery=conf.mastery,
        )
    if conf.damage_logic_type == "DEX":
        return DEXBasedDamageLogic(
            attack_range_constant=conf.attack_range_constant,
            mastery=conf.mastery,
        )
    if conf.damage_logic_type == "LUK":
        return LUKBasedDamageLogic(
            attack_range_constant=conf.attack_range_constant,
            mastery=conf.mastery,
        )
    if conf.damage_logic_type == "INT":
        return INTBasedDamageLogic(
            attack_range_constant=conf.attack_range_constant,
            mastery=conf.mastery,
        )

    raise ValueError(f"Unknown damage logic: {conf.damage_logic_type}")


def get_config(jobtype: JobType, combat_orders_level: int) -> DamageLogicConfiguration:
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
        DamageLogicConfiguration,
        loader.load(
            query={"group": jobtype.value, "kind": "DamageLogicConfiguration"},
            patches=patches,
        ),
    )


def get_damage_logic(jobtype: JobType, combat_orders_level: int) -> DamageLogic:
    conf = get_config(jobtype, combat_orders_level)
    return get_damage_logic_from_config(conf)
