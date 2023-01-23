from typing import Literal, Optional

from simaple.core import Stat, StatProps
from simaple.gear.gear import GearMeta
from simaple.gear.gear_type import GearType
from simaple.gear.improvements.base import GearImprovement
from simaple.gear.improvements.starforce_configuration import (
    GloveIncrementProvider,
    HpMpIncrementProvider,
    StarforceAttackIncrementProvider,
    StarforceIncrementProvider,
    StarforceStatIncrementProvider,
    SuperiorIncrementProvider,
    get_starforce_increment,
)


class Enhancement(GearImprovement):
    type: Literal["Enhancement"] = "Enhancement"
    star: int = 0
    enhancement_type: Literal["Starforce", "Amazing"]

    def max_star(self, meta: GearMeta) -> int:
        """
        Returns the number of gear's max star.
        :return: The number of gear's max star.
        """
        if meta.max_scroll_chance <= 0:
            return 0
        if meta.type.is_mechanic_gear() or meta.type.is_dragon_gear():
            return 0

        star_data = [
            [0, 5, 3],
            [95, 8, 5],
            [110, 10, 8],
            [120, 15, 10],
            [130, 20, 12],
            [140, 25, 15],
        ]

        data = None
        for item in star_data:
            if meta.req_level >= item[0]:
                data = item
            else:
                break
        if data is None:
            return 0
        return data[2 if meta.superior_eqp else 1]


class Starforce(Enhancement):
    enhancement_type: Literal["Starforce"] = "Starforce"

    def calculate_improvement(
        self, meta: GearMeta, ref_stat: Optional[Stat] = None
    ) -> Stat:
        if ref_stat is None:
            raise ValueError("Starforce may require referenced stat")

        current_improvement = Stat()
        for i in range(1, self.star + 1):
            current_improvement = (
                current_improvement
                + self.get_single_starforce_improvement(
                    meta, ref_stat, i, current_improvement
                )
            )

        return current_improvement

    def apply_star_cutoff(self, meta: GearMeta):
        self.star = min(self.star, self.max_star(meta))

    def get_single_starforce_improvement(
        self,
        meta: GearMeta,
        ref_stat: Stat,
        target_star: int,
        current_improvement: Stat,
    ) -> Stat:
        if target_star > self.max_star(meta):
            raise TypeError(
                f"Starforce improvement cannot exceed item constraint. Given {target_star} but maximum {self.max_star(meta)}"
            )

        current_gear_stat = current_improvement + ref_stat

        if meta.superior_eqp:
            return SuperiorIncrementProvider().get_increment(
                meta, target_star, current_gear_stat
            )

        improvement_stat = Stat()
        increment_providers: list[StarforceIncrementProvider] = [
            StarforceStatIncrementProvider(),
            StarforceAttackIncrementProvider(),
            HpMpIncrementProvider(),
            GloveIncrementProvider(),
        ]

        for increment_provider in increment_providers:
            improvement_stat += increment_provider.get_increment(
                meta, target_star, current_gear_stat
            )

        return improvement_stat


class AmazingEnhancement(Enhancement):
    enhancement_type: Literal["Amazing"] = "Amazing"
    bonus: bool = False

    def calculate_improvement(
        self, meta: GearMeta, ref_stat: Optional[Stat] = None
    ) -> Stat:
        current_improvement = Stat()
        if ref_stat is None:
            raise ValueError("Starforce may require referenced stat")

        for i in range(1, self.star + 1):
            current_improvement = (
                current_improvement
                + self.get_single_amazing_enhancement(meta, ref_stat, i)
            )

        return current_improvement

    def get_single_amazing_enhancement(
        self, meta: GearMeta, ref_stat: Stat, target_star: int
    ) -> Stat:
        if target_star >= self.max_star(meta):
            raise TypeError("Starforce improvement cannot exceed item constraint")

        improvement_stat = Stat()

        stat_enhancement_increment = get_starforce_increment(
            meta, target_star, amazing_scroll=True, att=False
        ) + self.stat_bonus(meta, target_star)

        for prop_type in (StatProps.STR, StatProps.DEX, StatProps.INT, StatProps.LUK):
            if ref_stat.get(prop_type) > 0:
                improvement_stat += Stat.parse_obj(
                    {prop_type.value: stat_enhancement_increment}
                )

        att_enhancement_increment = get_starforce_increment(
            meta, target_star, amazing_scroll=True, att=True
        ) + self.att_bonus(meta, target_star)

        for att_type in (StatProps.attack_power, StatProps.magic_attack):
            if ref_stat.get(att_type) > 0:
                improvement_stat += Stat.parse_obj(
                    {att_type.value: att_enhancement_increment}
                )
                if meta.type.is_improved_as_weapon():
                    improvement_stat += Stat.parse_obj(
                        {att_type.value: ref_stat.get(att_type) // 50 + 1}
                    )

        return improvement_stat

    def stat_bonus(self, meta: GearMeta, target_star: int):
        return (
            (2 if target_star > 5 else 1)
            if self.bonus and meta.type.is_accessory()
            else 0
        )

    def att_bonus(self, meta: GearMeta, target_star: int):
        return (
            1
            if self.bonus and (meta.type.is_weapon() or meta.type == GearType.shield)
            else 0
        )
