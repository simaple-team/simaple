from typing import Any

import pydantic
from loguru import logger

from simaple.core import Stat
from simaple.fetch.translator.base import AbstractStatProvider, NoMatchedStringError
from simaple.fetch.translator.potential import PotentialTranslator
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository
from simaple.gear.potential import AdditionalPotential


class GearStatTranslator(pydantic.BaseModel):
    patterns: dict[str, AbstractStatProvider]

    class Config:
        arbitrary_types_allowed = True

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


class GearTranslator(pydantic.BaseModel):
    gear_stat_translator: GearStatTranslator
    potential_translator: PotentialTranslator
    gear_repository: GearRepository

    class Config:
        arbitrary_types_allowed = True

    def translate(self, parsed: dict[str, Any]) -> Gear:
        gear_name: str = parsed["name"]
        base_gear = self._get_base_gear(gear_name)

        base_stat = self.gear_stat_translator.translate(parsed["base"])
        if base_stat != base_gear.stat:
            logger.warning(
                "Base stat not matched. Maybe fetched information incomplete?"
            )

        base_stat += self.gear_stat_translator.translate(parsed["bonus"])

        base_stat += self.gear_stat_translator.translate(parsed["increment"])

        base_gear = Gear(
            meta=base_gear.meta, stat=base_stat, scroll_chance=base_gear.scroll_chance
        )

        if "potential" in parsed:
            base_gear = base_gear.set_potential(
                self.potential_translator.translate(parsed["potential"]["raw"])
            )
        if "additional_potential" in parsed:
            base_gear = base_gear.set_additional_potential(
                AdditionalPotential(
                    options=self.potential_translator.translate(
                        parsed["additional_potential"]["raw"]
                    ).options
                )
            )

        return base_gear

    def _get_base_gear(self, gear_name: str) -> Gear:
        return self.gear_repository.get_by_name(gear_name)
