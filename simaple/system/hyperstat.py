from __future__ import annotations

from pydantic import BaseModel

from simaple.core import Stat, StatProps
from simaple.system.base import UpgradableUserStat


class HyperStatBasis(UpgradableUserStat): ...


class Hyperstat(BaseModel):
    options: list[tuple[StatProps, list[Stat]]]
    cost: list[int]
    levels: list[int]

    @classmethod
    def get_maximum_cost_from_level(cls, character_level: int) -> int:
        def get_character_level_point(character_level: int) -> int:
            return character_level // 10 - 11

        def get_sumation_with_ten_step_unit(character_level: int) -> int:
            return (
                (
                    get_character_level_point(140)
                    + get_character_level_point(character_level)
                    - 1
                )
                * (character_level // 10 - 14)
                * 5
            )

        if character_level < 140:
            return 0

        return get_sumation_with_ten_step_unit(
            character_level
        ) + get_character_level_point(character_level) * (character_level % 10 + 1)

    def length(self):
        return len(self.options)

    def get_cost_for_level(self, level: int) -> int:
        return sum(self.cost[:level])

    def get_current_cost(self) -> int:
        return sum(self.get_cost_for_level(lv) for lv in self.levels)

    def get_stat(self) -> Stat:
        return sum(
            [option[lv] for (_, option), lv in zip(self.options, self.levels)], Stat()
        )

    def set_level(self, stat_type: StatProps, level: int) -> Hyperstat:
        for i, (prop, _) in enumerate(self.options):
            if prop == stat_type:
                levels = self.levels.copy()
                levels[i] = level
                return Hyperstat(
                    options=self.options,
                    cost=self.cost,
                    levels=levels,
                )

        raise ValueError(f"Given Stat Type {stat_type} does not exist in hyperstat")

    def get_level_rearranged(self, levels: list[int]) -> Hyperstat:
        assert len(levels) == self.length()

        return Hyperstat(
            options=self.options,
            cost=self.cost,
            levels=levels,
        )
