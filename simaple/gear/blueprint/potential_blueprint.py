import enum
import os
from typing import Optional, TypedDict

import yaml
from pydantic import BaseModel

from simaple.core.base import ExtendedStat, Stat
from simaple.gear.potential import Potential, PotentialTier


class PotentialType(enum.Enum):
    normal = "normal"
    additional = "additional"
    normal_weapon = "normal_weapon"
    additional_weapon = "additional_weapon"

    @classmethod
    def get_type(cls, is_additional: bool, is_weapon: bool) -> "PotentialType":
        if is_additional:
            if is_weapon:
                return PotentialType.additional_weapon

            return PotentialType.additional

        if is_weapon:
            return PotentialType.normal_weapon

        return PotentialType.normal


class PotentialFieldName(enum.Enum):
    DEX_multiplier = "DEX_multiplier"
    STR_multiplier = "STR_multiplier"
    LUK_multiplier = "LUK_multiplier"
    INT_multiplier = "INT_multiplier"

    STR = "STR"
    DEX = "DEX"
    LUK = "LUK"
    INT = "INT"

    MHP = "MHP"
    MMP = "MMP"
    MHP_multiplier = "MHP_multiplier"
    MMP_multiplier = "MMP_multiplier"

    magic_attack = "magic_attack"
    attack_power = "attack_power"

    boss_damage_multiplier = "boss_damage_multiplier"
    all_stat_multiplier = "all_stat_multiplier"
    damage_multiplier = "damage_multiplier"
    ignored_defence = "ignored_defence"
    all_stat = "all_stat"

    attack_power_multiplier = "attack_power_multiplier"
    magic_attack_multiplier = "magic_attack_multiplier"
    critical_damage = "critical_damage"
    critical_rate = "critical_rate"


_PotentialSet = dict[PotentialFieldName, dict[str, int]]


class PotentialQuery(TypedDict):
    level: int
    type: PotentialType
    tier: PotentialTier
    name: PotentialFieldName


class PotentialTierTable:
    def __init__(
        self, db: dict[PotentialType, dict[PotentialTier, list[_PotentialSet]]]
    ) -> None:
        self._db = db

    def empty(self) -> bool:
        return len(self._db) == 0

    @classmethod
    def kms(cls) -> "PotentialTierTable":
        return _global_load_kms_potential_table()

    def get(self, query: PotentialQuery) -> ExtendedStat:
        tier_mapping = self._db[query["type"]]

        effect_list = tier_mapping[query["tier"]]
        effect = effect_list[self._get_effect_index(query["level"])]
        stat = effect[query["name"]]

        return ExtendedStat(stat=Stat.model_validate(stat))

    def _get_effect_index(self, level: int) -> int:
        return int((level - 1) // 10)


__potential_db_table: PotentialTierTable = PotentialTierTable({})


def _global_load_kms_potential_table() -> PotentialTierTable:
    global __potential_db_table  # pylint:disable=W0603
    if __potential_db_table.empty():
        table_path = os.path.join(os.path.dirname(__file__), "db.yaml")

        with open(table_path, encoding="utf-8") as f:
            untyped_db = yaml.safe_load(f)

        db: dict[PotentialType, dict[PotentialTier, list[_PotentialSet]]] = {}
        for type_key, raw_type_db in untyped_db.items():
            tier_mapping = {}
            for tier_key, raw_tier_db in raw_type_db.items():
                potential_sets = [
                    {PotentialFieldName(k): v for k, v in name_stat_map.items()}
                    for name_stat_map in raw_tier_db
                ]
                tier_mapping[PotentialTier(tier_key)] = potential_sets

            db[PotentialType(type_key)] = tier_mapping

        __potential_db_table = PotentialTierTable(db)

    return __potential_db_table


class PotentialField(BaseModel):
    name: PotentialFieldName
    value: Optional[int] = None
    tier: Optional[PotentialTier] = None


class PotentialTemplate(BaseModel):
    options: list[PotentialField] = []


def field_to_value(
    field: PotentialField,
    table: PotentialTierTable,
    level: int,
    potential_type: PotentialType,
) -> ExtendedStat:
    if field.value:
        return ExtendedStat(stat=Stat.model_validate({field.name.value: field.value}))

    if not field.tier:
        raise ValueError("value for tier must be given")

    return table.get(
        {
            "name": field.name,
            "level": level,
            "type": potential_type,
            "tier": field.tier,
        }
    )


def template_to_potential(
    spec: PotentialTemplate,
    table: PotentialTierTable,
    level: int,
    potential_type: PotentialType,
) -> Potential:
    return Potential(
        options=[
            field_to_value(field, table, level, potential_type)
            for field in spec.options
        ]
    )
