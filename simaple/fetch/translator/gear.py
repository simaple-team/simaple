from typing import Any

import pydantic
from loguru import logger

from simaple.core import Stat
from simaple.fetch.translator.base import AbstractStatProvider, NoMatchedStringError
from simaple.fetch.translator.potential import PotentialTranslator
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository
from simaple.gear.gear_type import GearType
from simaple.gear.potential import Potential


class GearStatTranslator(pydantic.BaseModel):
    patterns: dict[str, AbstractStatProvider]

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def translate(self, parsed_stat: dict[str, int]) -> Stat:
        stat = Stat()
        for keyword, dependency in parsed_stat.items():
            try:
                value = self.patterns[keyword].provide(dependency)
                if not isinstance(value, Stat):
                    raise RuntimeError(
                        "Provided value for gear must be Stat, not ActionStat or LevelStat."
                    )
                stat += value
            except KeyError as e:
                raise NoMatchedStringError from e

        return stat


def _replace_as_static_if_arcane_symbol(stat: Stat, gear: Gear) -> Stat:
    if gear.meta.type == GearType.arcane_symbol:
        return Stat(
            STR_static=stat.STR,
            DEX_static=stat.DEX,
            INT_static=stat.INT,
            LUK_static=stat.LUK,
        )

    return stat


class GearTranslator(pydantic.BaseModel):
    gear_stat_translator: GearStatTranslator
    potential_translator: PotentialTranslator
    gear_repository: GearRepository

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    def translate(self, parsed: dict[str, Any]) -> Gear:
        gear_name: str = parsed["name"]
        base_gear = self._get_base_gear(gear_name)

        base_stat = _replace_as_static_if_arcane_symbol(
            self.gear_stat_translator.translate(parsed.get("base", {})),
            base_gear,
        )

        if base_stat != base_gear.stat:
            logger.warning(
                f"{gear_name} Base stat not matched. Maybe fetched information incomplete?"
            )
            logger.warning(
                f"Was {base_stat.short_dict()}, but {base_gear.stat.short_dict()}"
            )
            if base_gear.meta.type != GearType.dummy:
                base_stat = base_gear.meta.base_stat

        base_stat += _replace_as_static_if_arcane_symbol(
            self.gear_stat_translator.translate(parsed.get("bonus", {})),
            base_gear,
        )
        base_stat += _replace_as_static_if_arcane_symbol(
            self.gear_stat_translator.translate(parsed.get("increment", {})),
            base_gear,
        )
        if "soulweapon" in parsed:
            base_stat += self.gear_stat_translator.translate(
                parsed["soulweapon"]["option"]
            )

        base_gear = Gear(
            meta=base_gear.meta, stat=base_stat, scroll_chance=base_gear.scroll_chance
        )

        if "potential" in parsed:
            base_gear = base_gear.set_potential(
                self.potential_translator.translate(parsed["potential"]["raw"])
            )
        if "additional_potential" in parsed:
            base_gear = base_gear.set_additional_potential(
                Potential(
                    options=self.potential_translator.translate(
                        parsed["additional_potential"]["raw"]
                    ).options
                )
            )

        return base_gear

    def _get_base_gear(self, gear_name: str) -> Gear:
        return self.gear_repository.get_by_name(
            gear_name, create_empty_item_if_not_exist=True
        )
