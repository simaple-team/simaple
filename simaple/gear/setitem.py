from __future__ import annotations

import json
import os
from abc import ABCMeta, abstractmethod
from typing import Iterable, List, Optional, Set, Tuple, TypedDict

from pydantic import BaseModel

from simaple.core import Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository

SET_ITEM_RESOURCE_PATH = os.path.join(
    os.path.dirname(__file__), "resources", "set_item.json"
)


class SetItem(BaseModel):
    id: int = 0
    name: str
    joker_possible: bool = False
    gears: list[Gear] = []
    effects: list[Stat] = []

    def get_effect(self, count) -> Stat:
        return sum(
            [self.effects[i] for i in range(min(len(self.effects), count + 1))], Stat()
        )

    def gear_ids(self) -> List[int]:
        return [v.meta.id for v in self.gears]

    def count(self, gears: Iterable[Gear], joker_gear: Optional[Gear] = None) -> int:
        count = 0
        applied_types = []
        existing_types = [g.meta.type for g in self.gears]
        for gear in gears:
            if gear.meta.id in self.gear_ids():
                count += 1
                applied_types.append(gear.meta.type)

        if (
            joker_gear is not None
            and joker_gear.meta.type not in applied_types
            and joker_gear.meta.type in existing_types
            and count >= 3
        ):
            count += 1

        return count

    def measure(self, other_set_items: List[SetItem], gears: List[Gear]) -> int:
        def _get_set_item_basis(_set_items, _gears, _joker_gear=None) -> int:
            return sum(
                [
                    set_item.count(_gears, joker_gear=_joker_gear)
                    for set_item in _set_items
                ]
            )

        joker_gears = [gear for gear in gears if gear.meta.joker_to_set_item]
        joker_gears.sort(key=lambda x: x.meta.id)

        if len(joker_gears) > 0:
            set_item_count_basis = _get_set_item_basis(other_set_items, gears)
            for joker_gear in joker_gears:
                current_count_basis = _get_set_item_basis(
                    other_set_items, gears, _joker_gear=joker_gear
                )
                if current_count_basis > set_item_count_basis:
                    return self.count(gears, joker_gear=joker_gear)

        return self.count(gears)


class SetItemRepository(metaclass=ABCMeta):
    @abstractmethod
    def get(self, set_item_id) -> SetItem: ...

    @abstractmethod
    def get_all(self, gears: Iterable[Gear]) -> list[SetItem]: ...


class WzresourceStatRepresentation(TypedDict, total=False):
    incAllStat: int

    incPAD: int
    incMAD: int

    incMHP: int
    incMMP: int

    incCriticaldamage: int

    incSTR: int
    incDEX: int
    incINT: int
    incLUK: int

    ignoreTargetDEF: int
    incBDR: int
    incDAMr: int


class WzresourceSetItemEntity(TypedDict):
    name: str
    items: list[int]
    effect: dict[str, WzresourceStatRepresentation]
    jokerPossible: bool


class KMSSetItemRepository(SetItemRepository):
    def __init__(self):
        self._gear_repository = GearRepository()
        self._load()

    def _load(self):
        with open(SET_ITEM_RESOURCE_PATH, encoding="utf-8") as f:
            self._set_items = json.load(f)

    def _interpret_stat(self, raw_stat: WzresourceStatRepresentation):
        stat = Stat()
        stat += Stat.all_stat(raw_stat.get("incAllStat", 0))
        stat += Stat(
            attack_power=raw_stat.get("incPAD", 0),
            magic_attack=raw_stat.get("incMAD", 0),
            MHP=raw_stat.get("incMHP", 0),
            MMP=raw_stat.get("incMMP", 0),
            critical_damage=raw_stat.get("incCriticaldamage", 0),
            STR=raw_stat.get("incSTR", 0),
            DEX=raw_stat.get("incDEX", 0),
            INT=raw_stat.get("incINT", 0),
            LUK=raw_stat.get("incLUK", 0),
            boss_damage_multiplier=raw_stat.get("incBDR", 0),
            ignored_defence=raw_stat.get("ignoreTargetDEF", 0),
            damage_multiplier=raw_stat.get("incDAMr", 0),
        )
        return stat

    def _parse_from_raw(
        self, set_item_id: int, raw_set_item: WzresourceSetItemEntity
    ) -> SetItem:
        maximum_effects = max(map(int, raw_set_item["effect"].keys()))
        effects = [Stat() for i in range(maximum_effects + 1)]

        for index, prop in raw_set_item["effect"].items():
            effects[int(index)] = self._interpret_stat(prop)

        return SetItem(
            effects=effects,
            gears=[
                self._gear_repository.get_by_id(int(gear_id))
                for gear_id in raw_set_item["items"]
                if self._gear_repository.exists(gear_id)
            ],
            name=raw_set_item["name"],
            id=set_item_id,
            joker_possible=raw_set_item.get("jokerPossible", False),
        )

    def get_all(self, gears: Iterable[Gear]) -> list[SetItem]:
        set_items = []

        for set_item_id in self._set_items:
            set_item = self.get(set_item_id)
            if set_item.count(gears) > 0:
                set_items.append(set_item)

        return set_items

    def get(self, set_item_id: int) -> SetItem:
        return self._parse_from_raw(
            set_item_id,
            self._set_items[str(set_item_id)],
        )

    def get_set_item_counts(self, gears: List[Gear]) -> List[Tuple[SetItem, int]]:
        """
        Return List of (set_item, count).
        """
        set_item_ids: Set[int] = set()
        for gear in gears:
            if gear.meta.set_item_id != 0:
                set_item_ids.update([gear.meta.set_item_id])

        existing_set_items = [self.get(set_item_id) for set_item_id in set_item_ids]

        return [
            (set_item, set_item.measure(existing_set_items, gears))
            for set_item in existing_set_items
        ]
