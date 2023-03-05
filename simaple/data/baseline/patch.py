import json
import os

import pydantic

from simaple.core import JobCategory, JobType
from simaple.gear.bonus_factory import BonusType
from simaple.gear.gear_repository import GearRepository
from simaple.spec.patch import DFSTraversePatch, KeywordExtendPatch, Patch, StringPatch


def kms_item_alias():
    INTERPETER_RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "resources")
    path = os.path.join(INTERPETER_RESOURCE_PATH, "item_name_alias.json")

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def kms_weapon_alias():
    INTERPETER_RESOURCE_PATH = os.path.join(os.path.dirname(__file__), "resources")
    path = os.path.join(INTERPETER_RESOURCE_PATH, "weapon_name_alias.json")

    with open(path, encoding="utf-8") as f:
        return json.load(f)


class GearIdPatch(Patch):
    job_category: JobCategory
    job_type: JobType
    item_name_alias: dict[str, list[str]] = pydantic.Field(
        default_factory=kms_item_alias
    )
    weapon_name_alias: dict[str, dict[str, str]] = pydantic.Field(
        default_factory=kms_weapon_alias
    )
    repository: GearRepository = pydantic.Field(default_factory=GearRepository)

    class Config:
        arbitrary_types_allowed = True

    def interpret_gear_id(self, name: str) -> str:
        if name in self.item_name_alias:
            return self.item_name_alias[name][self.job_category.value]

        if name in self.weapon_name_alias:
            return self.weapon_name_alias[name][self.job_type.value]

        return name

    def apply(self, raw):
        if isinstance(raw, list):
            return [self.apply(arg) for arg in raw]

        if isinstance(raw, (int, float, str)):
            return raw

        interpreted = {}

        for k, v in raw.items():
            if isinstance(v, (dict, list)):
                interpreted[k] = self.apply(v)
            else:
                if k == "gear_id":
                    gear = self.repository.get_by_name(self.interpret_gear_id(v))
                    interpreted["meta"] = gear.meta.dict()
                else:
                    interpreted[k] = v

        return interpreted


class DoubleBonusRefinePatch(DFSTraversePatch):
    def patch_value(self, value, origin: dict):
        return BonusType.refine_double_key(value)

    def patch_dict(self, k, v, origin: dict):
        return {k: BonusType.refine_double_key(v)}


def all_stat_patch():
    return KeywordExtendPatch(
        target_keyword="all_stat", extends=["STR", "DEX", "INT", "LUK"]
    )


def all_att_patch():
    return KeywordExtendPatch(
        target_keyword="all_att", extends=["attack_power", "magic_attack"]
    )


def stat_patch(stat_priority: tuple[str, str, str, str]):
    return StringPatch(
        as_is=["first_stat", "second_stat", "third_stat", "fourth_stat"],
        to_be=stat_priority,
    )


def attack_patch(attack_priority: tuple[str, str]):
    return StringPatch(as_is=["first_att", "second_att"], to_be=attack_priority)
