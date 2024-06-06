from __future__ import annotations

from pydantic import BaseModel

from simaple.core import Stat, StatProps
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository
from simaple.system.base import HyperStatBasis
from simaple.system.hyperstat import HyperStatBasis


def get_hyperstat_from_spec() -> dict[str, HyperStatBasis]:
    repository = DirectorySpecRepository("simaple/data/system")
    loader = SpecBasedLoader(repository)

    hyperstat_basis: list[HyperStatBasis] = loader.load_all(
        query={"kind": "UpgradableUserStat"},
    )

    return {basis.name: basis for basis in hyperstat_basis}


HYPERSTAT_BASIS = {
    StatProps(k): [ex_stat.stat for ex_stat in v.values]
    for k, v in get_hyperstat_from_spec().items()
}

HYPERSTAT_COST = [1, 2, 4, 8, 10, 15, 20, 25, 30, 35, 50, 65, 80, 95, 110, 999999]


def get_hyperstat_lists() -> list[tuple[StatProps, list[Stat]]]:
    return list(sorted(HYPERSTAT_BASIS.items(), key=lambda x: x[0].value))


def get_empty_hyperstat_levels() -> list[int]:
    return [0 for i in range(len(HYPERSTAT_BASIS))]


def get_hyperstat_cost() -> list[int]:
    return list(HYPERSTAT_COST)


def get_kms_hyperstat() -> Hyperstat:
    return Hyperstat(
        options=get_hyperstat_lists(),
        cost=get_hyperstat_cost(),
        levels=get_empty_hyperstat_levels(),
    )


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
