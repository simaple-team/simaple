from collections import defaultdict

from pydantic import BaseModel, Field, model_validator

from simaple.core import Stat
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


class HexaStatCoreType(
    BaseModel, metaclass=TaggedNamespacedABCMeta(kind="HexaStatCore")
):
    name: str
    basis: dict[str, float]

    def _get_main_stat_multiplier(self, level: int) -> int:
        return [0, 1, 2, 3, 4, 6, 8, 10, 13, 16, 20][level]

    def get_main_stat_effect(self, level: int) -> Stat:
        return Stat.model_validate(
            {
                stat_name: stat_value * self._get_main_stat_multiplier(level)
                for stat_name, stat_value in self.basis.items()
            }
        )

    def get_sub_stat_effect(self, level: int) -> Stat:
        return Stat.model_validate(
            {
                stat_name: stat_value * level
                for stat_name, stat_value in self.basis.items()
            }
        )


class HexaStatCore(BaseModel):
    main_stat_name: str
    sub_stat_name_1: str
    sub_stat_name_2: str

    main_stat_level: int
    sub_stat_level_1: int
    sub_stat_level_2: int


class HexaStat(BaseModel):
    core_types: list[HexaStatCoreType]

    cores: list[HexaStatCore]

    def get_stat(self) -> Stat:
        _core_types_map = {core_type.name: core_type for core_type in self.core_types}

        stat = Stat()
        for core in self.cores:
            stat += _core_types_map[core.main_stat_name].get_main_stat_effect(
                core.main_stat_level
            )

            stat += _core_types_map[core.sub_stat_name_1].get_sub_stat_effect(
                core.sub_stat_level_1
            )
            stat += _core_types_map[core.sub_stat_name_2].get_sub_stat_effect(
                core.sub_stat_level_2
            )

        return stat
