from abc import ABCMeta, abstractmethod

from simaple.core import Stat, StatProps
from simaple.gear.gear import GearMeta
from simaple.gear.gear_type import GearType

# fmt: off
__superior_att_increments = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [110, 0, 0, 0, 0, 0, 5, 6, 7, 0, 0, 0, 0, 0, 0, 0],
    [150, 0, 0, 0, 0, 0, 9, 10, 11, 12, 13, 15, 17, 19, 21, 23],
]
__superior_stat_increments = [
    [0, 1, 2, 4, 7, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [80, 2, 3, 5, 8, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [110, 9, 10, 12, 15, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [150, 19, 20, 22, 25, 29, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
__starforce_weapon_att_increments = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [108, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 5, 6, 7, 8, 9, 27, 28, 29],
    [118, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 6, 7, 8, 9, 10, 28, 29, 30],
    [128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 7, 7, 8, 9, 10, 11, 29, 30, 31],
    [138, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 8, 8, 9, 10, 11, 12, 30, 31, 32],
    [148, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 9, 10, 11, 12, 13, 31, 32, 33],
    [158, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 10, 11, 12, 13, 14, 32, 33, 34],
    [198, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 13, 14, 14, 15, 16, 17, 34, 35, 36],
]
__starforce_att_increments = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [108, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 9, 10, 12, 13, 15, 17],
    [118, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 7, 8, 9, 10, 11, 13, 14, 16, 18],
    [128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20],
    [138, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 10, 11, 12, 13, 15, 17, 19, 21],
    [148, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22],
    [158, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 11, 12, 13, 14, 15, 17, 19, 21, 23],
    [198, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 13, 14, 15, 16, 17, 19, 21, 23, 25],
]
__starforce_stat_increments = [
    [0, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [108, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0],
    [118, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0],
    [128, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0],
    [138, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0],
    [148, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 11, 11, 11, 11, 11, 11, 11, 0, 0, 0],
    [158, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 13, 13, 13, 13, 13, 13, 13, 0, 0, 0],
    [198, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 15, 15, 15, 15, 15, 15, 15, 0, 0, 0],
]
__amazing_att_increments = [
    [0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14],
    [80, 0, 0, 0, 0, 0, 2, 3, 4, 5, 6, 7, 9, 11, 13, 15],
    [90, 0, 0, 0, 0, 0, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16],
    [100, 0, 0, 0, 0, 0, 4, 5, 6, 7, 8, 9, 11, 13, 15, 17],
    [110, 0, 0, 0, 0, 0, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18],
    [120, 0, 0, 0, 0, 0, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19],
    [130, 0, 0, 0, 0, 0, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20],
    [140, 0, 0, 0, 0, 0, 8, 9, 10, 11, 12, 13, 15, 17, 19, 21],
    [150, 0, 0, 0, 0, 0, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22],
]
__amazing_stat_increments = [
    [0, 1, 2, 4, 7, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [80, 2, 3, 5, 8, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [85, 3, 4, 6, 9, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [90, 4, 5, 7, 10, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [95, 5, 6, 8, 11, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [100, 7, 8, 10, 13, 17, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [105, 8, 9, 11, 14, 18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [110, 9, 10, 12, 15, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [115, 10, 11, 13, 16, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [120, 12, 13, 15, 18, 22, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [125, 13, 14, 16, 19, 23, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [130, 14, 15, 17, 20, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [135, 15, 16, 18, 21, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [140, 17, 18, 20, 23, 27, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [145, 18, 19, 21, 24, 28, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [150, 19, 20, 22, 25, 29, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


_glove_starforce_bonus = [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

_mhp_starforce_bonus = [0, 5, 5, 5, 10, 10, 15, 15, 20, 20, 25, 25, 25, 25, 25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# fmt: on


class StarforceIncrementProvider(metaclass=ABCMeta):
    @abstractmethod
    def get_increment(
        self, meta: GearMeta, target_star: int, current_gear_stat: Stat
    ) -> Stat:
        ...


class StarforceStatIncrementProvider(StarforceIncrementProvider):
    def get_increment(
        self, meta: GearMeta, target_star: int, current_gear_stat: Stat
    ) -> Stat:
        # Add Basis stats (STR, DEX, INT, LUK)
        increment = Stat()
        target_stats = self._get_target_stats(meta)
        stat_starforce_increment = get_starforce_increment(
            meta, target_star, amazing_scroll=False, att=False
        )

        for prop_type in (StatProps.STR, StatProps.DEX, StatProps.INT, StatProps.LUK):
            if prop_type in target_stats or (
                target_star > 15 and current_gear_stat.get(prop_type) > 0
            ):
                increment += Stat.parse_obj({prop_type.value: stat_starforce_increment})

        return increment

    def _get_target_stats(self, meta: GearMeta) -> set[StatProps]:
        stat_set: set[StatProps] = set()
        job_stat = [
            [StatProps.STR, StatProps.DEX],
            [StatProps.INT, StatProps.LUK],
            [StatProps.DEX, StatProps.STR],
            [StatProps.LUK, StatProps.DEX],
            [StatProps.STR, StatProps.DEX],
        ]

        if meta.req_job == 0:
            stat_set = {StatProps.STR, StatProps.DEX, StatProps.INT, StatProps.LUK}
        else:
            for i in range(0, 5):
                if meta.req_job & (1 << i) != 0:
                    for prop_type in job_stat[i]:
                        stat_set.add(prop_type)

        return stat_set


class StarforceAttackIncrementProvider(StarforceIncrementProvider):
    def get_increment(
        self, meta: GearMeta, target_star: int, current_gear_stat: Stat
    ) -> Stat:
        # Add attack props (attack_power, magic_attack)
        if meta.type.is_improved_as_weapon():
            return self._get_weapon_starforce_increment(
                meta, target_star, current_gear_stat
            )

        att_starforce_increment = get_starforce_increment(
            meta, target_star, amazing_scroll=False, att=True
        )

        return Stat(
            attack_power=att_starforce_increment,
            magic_attack=att_starforce_increment,
        )

    def _get_weapon_starforce_increment(
        self, meta: GearMeta, target_star: int, current_gear_stat: Stat
    ) -> Stat:
        improvement_stat = Stat()
        att_starforce_increment = get_starforce_increment(
            meta, target_star, amazing_scroll=False, att=True
        )

        use_mad = (
            meta.req_job == 0
            or meta.req_job // 2 % 2 == 1
            or current_gear_stat.magic_attack > 0
        )
        if target_star > 15:
            improvement_stat += Stat(attack_power=att_starforce_increment)
            if use_mad:
                improvement_stat += Stat(magic_attack=att_starforce_increment)
        else:
            improvement_stat += Stat(
                attack_power=current_gear_stat.attack_power // 50 + 1
            )
            if use_mad:
                improvement_stat += Stat(
                    magic_attack=current_gear_stat.magic_attack // 50 + 1
                )

        return improvement_stat


class GloveIncrementProvider(StarforceIncrementProvider):
    def get_increment(self, meta: GearMeta, target_star: int, _: Stat) -> Stat:
        if meta.type != GearType.glove:
            return Stat()

        bonus = _glove_starforce_bonus[target_star]

        if meta.req_job == 0:
            return Stat(
                attack_power=bonus,
                magic_attack=bonus,
            )
        if meta.req_job // 2 % 2 == 1:
            return Stat(
                magic_attack=bonus,
            )

        return Stat(
            attack_power=bonus,
        )


class HpMpIncrementProvider(StarforceIncrementProvider):
    def get_increment(self, meta: GearMeta, target_star: int, _: Stat) -> Stat:
        bonus = _mhp_starforce_bonus[target_star]

        if meta.type.is_improved_as_weapon():
            return Stat(
                MHP=bonus,
                MMP=bonus,
            )
        if meta.type in [
            GearType.cap,
            GearType.coat,
            GearType.longcoat,
            GearType.pants,
            GearType.cape,
            GearType.ring,
            GearType.pendant,
            GearType.belt,
            GearType.shoulder_pad,
            GearType.shield,
        ]:
            return Stat(MHP=bonus)

        return Stat()


class SuperiorIncrementProvider(StarforceIncrementProvider):
    def get_increment(self, meta: GearMeta, target_star: int, _: Stat) -> Stat:
        stat_starforce_increment = get_starforce_increment(
            meta, target_star, amazing_scroll=True, att=False
        )
        att_starforce_increment = get_starforce_increment(
            meta, target_star, amazing_scroll=True, att=True
        )

        return Stat(
            attack_power=att_starforce_increment,
            magic_attack=att_starforce_increment,
            LUK=stat_starforce_increment,
            STR=stat_starforce_increment,
            INT=stat_starforce_increment,
            DEX=stat_starforce_increment,
        )


class AmazingStatIncrementProvider(StarforceIncrementProvider):
    def __init__(self, bonus) -> None:
        self._bonus = bonus

    def get_increment(
        self, meta: GearMeta, target_star: int, current_gear_stat: Stat
    ) -> Stat:
        stat_enhancement_increment = get_starforce_increment(
            meta, target_star, amazing_scroll=True, att=False
        ) + self._get_stat_bonus(meta, target_star)

        increment = Stat()

        for prop_type in (StatProps.STR, StatProps.DEX, StatProps.INT, StatProps.LUK):
            if current_gear_stat.get(prop_type) > 0:
                increment += Stat.parse_obj(
                    {prop_type.value: stat_enhancement_increment}
                )

        return increment

    def _get_stat_bonus(self, meta: GearMeta, target_star: int):
        return (
            (2 if target_star > 5 else 1)
            if self._bonus and meta.type.is_accessory()
            else 0
        )


class AmazingAttackIncrementProvider(StarforceIncrementProvider):
    def get_increment(self, meta: GearMeta, target_star: int, _: Stat) -> Stat:
        ...


class StarforceIndex:
    def __init__(self, values: list[list[int]]):
        self._values = values

    def get_value(self, level: int, target_star: int):
        for item in reversed(self._values):
            if level >= item[0]:
                return item[target_star]

        raise ValueError("Given setting not available")


def get_starforce_increment(
    meta: GearMeta, target_star: int, amazing_scroll: bool, att: bool
) -> int:
    if meta.superior_eqp:
        if att:
            data = __superior_att_increments
        else:
            data = __superior_stat_increments
    elif not amazing_scroll:
        if att:
            if meta.type.is_improved_as_weapon():
                data = __starforce_weapon_att_increments
            else:
                data = __starforce_att_increments
        else:
            data = __starforce_stat_increments
    else:
        if att:
            data = __amazing_att_increments
        else:
            data = __amazing_stat_increments

    for item in reversed(data):
        if meta.req_level >= item[0]:
            return item[target_star]

    raise ValueError("Given setting not available")
