from __future__ import annotations

from pydantic import BaseModel

from simaple.core import Stat

HYPERSTAT_BASIS: dict[str, list[Stat]] = {
    "STR_static": [Stat(STR_static=i * 30) for i in range(16)],
    "DEX_static": [Stat(DEX_static=i * 30) for i in range(16)],
    "LUK_static": [Stat(LUK_static=i * 30) for i in range(16)],
    "INT_static": [Stat(INT_static=i * 30) for i in range(16)],
    "attacks": [Stat(attack_power=i * 3, magic_attack=i * 3) for i in range(16)],
    "damage_multiplier": [Stat(damage_multiplier=i * 3) for i in range(16)],
    "boss_damage_multiplier": [
        Stat(boss_damage_multiplier=i * 3 + max(i - 5, 0)) for i in range(16)
    ],
    "critical_damage": [Stat(critical_damage=i) for i in range(16)],
    "critical_rate": [Stat(critical_rate=i + max(i - 5, 0)) for i in range(16)],
    "ignored_defence": [Stat(ignored_defence=i * 3) for i in range(16)],
}

HYPERSTAT_COST = [1, 2, 4, 8, 10, 15, 20, 25, 30, 35, 50, 65, 80, 95, 110, 999999]


def get_hyperstat_lists() -> list[list[Stat]]:
    return [value_list for _, value_list in HYPERSTAT_BASIS.items()]


def get_empty_hyperstat_levels() -> list[int]:
    return [0 for i in range(len(HYPERSTAT_BASIS))]


def get_hyperstat_cost() -> list[int]:
    return list(HYPERSTAT_COST)


class Hyperstat(BaseModel):
    options: list[list[Stat]] = get_hyperstat_lists()
    cost: list[int] = get_hyperstat_cost()
    levels: list[int] = get_empty_hyperstat_levels()

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
            [option[lv] for option, lv in zip(self.options, self.levels)], Stat()
        )

    def get_level_rearranged(self, levels: list[int]) -> Hyperstat:
        assert len(levels) == self.length()

        return Hyperstat(
            options=self.options,
            cost=self.cost,
            levels=levels,
        )
