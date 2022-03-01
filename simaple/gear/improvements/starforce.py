from simaple.core.base import Stat, StatProps
from pydantic import BaseModel, conint
from simaple.gear.gear_type import GearType
from simaple.gear.gear import Gear
from simaple.gear.improvements.base import GearImprovement

from typing import Literal, List

import enum
import math


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



def get_starforce_increment(gear: Gear, target_star: int, amazing_scroll: bool, att: bool) -> int:
    if gear.superior_eqp:
        if att:
            data = __superior_att_increments
        else:
            data = __superior_stat_increments
    elif not amazing_scroll:
        if att:
            if gear.is_weapon() or gear.type == GearType.katara:
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
        if gear.req_level >= item[0]:
            return item[target_star]

    raise ValueError("Given setting not available")


class Starforce(BaseModel):
    type: Literal['Starforce'] = 'Starforce'
    star: int

    def max_star(self, gear: Gear) -> int:
        """
        Returns the number of gear's max star.
        :return: The number of gear's max star.
        """
        if gear.scroll_chance <= 0:
            return 0
        if gear.is_mechanic_gear() or gear.is_dragon_gear():
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
            if gear.req_level >= item[0]:
                data = item
            else:
                break
        if data is None:
            return 0
        return data[2 if gear.superior_eqp else 1]


    def calculate_improvement(self, gear) -> int:
        """
        Apply multiple stars and corresponding stats.
        :param count: Number for stars to apply.
        :param amazing_scroll: True to apply blue star; False to apply yellow star.
        :param bonus: True to apply bonus stat to blue star; False otherwise.
        :return: Number of increased stars.
        :raises AttributeError: If gear is not set.
        """
        current_improvement = Stat()
        for i in range(1, self.star + 1):
            current_improvement = current_improvement + self.get_single_starforce_improvement(gear, i, current_improvement)
        return current_improvement

    def get_single_starforce_improvement(self, gear: Gear, target_star: int, current_improvement: Stat) -> Stat:
        """
        Apply single star and corresponding stats.
        :param amazing_scroll: True to apply blue star; False to apply yellow star.
        :param bonus: True to apply bonus stat to blue star; False otherwise.
        :return: True if applied; False otherwise.
        :raises AttributeError: If gear is not set.
        """
        if target_star >= self.max_star(gear):
            raise TypeError('Starforce improvement cannot exceed item constraint')

        stat_starforce_increment = get_starforce_increment(gear, target_star, amazing_scroll=False, att=False)
        att_starforce_increment = get_starforce_increment(gear, target_star, amazing_scroll=False, att=True)
        current_gear_stat = current_improvement + gear.stat


        is_weapon = gear.is_weapon() or gear.type == GearType.katara

        job_stat = [
            [StatProps.STR, StatProps.DEX],
            [StatProps.INT, StatProps.LUK],
            [StatProps.DEX, StatProps.STR],
            [StatProps.LUK, StatProps.DEX],
            [StatProps.STR, StatProps.DEX],
        ]
        stat_set: Set[StatProps]

        improvement_stat = Stat()

        req_job = gear.req_job
        if req_job == 0:
            stat_set = {StatProps.STR, StatProps.DEX, StatProps.INT, StatProps.LUK}
        else:
            stat_set = set()
            for i in range(0, 5):
                if req_job & (1 << i) != 0:
                    for prop_type in job_stat[i]:
                        stat_set.add(prop_type)


        for prop_type in (StatProps.STR, StatProps.DEX, StatProps.INT, StatProps.LUK):
            if prop_type in stat_set or (target_star > 15 and current_gear_stat.get(prop_type.value) > 0):
                improvement_stat += Stat.parse_obj({prop_type.value: stat_starforce_increment})

        if is_weapon:
            use_mad = req_job == 0 or req_job // 2 % 2 == 1 or current_gear_stat.magic_attack > 0
            if target_star > 15:
                improvement_stat += Stat(attack_power=att_starforce_increment)
                if use_mad:
                    improvement_stat += Stat(magic_attack=att_starforce_increment)
            else:
                improvement_stat += Stat(attack_power=current_gear_stat.attack_power // 50 + 1)
                if use_mad:
                    improvement_stat += Stat(magic_attack=current_gear_stat.magic_attack // 50 + 1)
        else:
            improvement_stat += Stat(attack_power=att_starforce_increment, magic_attack=att_starforce_increment)
            if gear.type == GearType.glove:
                glove_bonus = [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                if req_job == 0:
                    improvement_stat += Stat(
                        attack_power=glove_bonus[target_star],
                        magic_attack=glove_bonus[target_star],
                    )
                elif req_job // 2 % 2 == 1:
                    improvement_stat += Stat(
                        magic_attack=glove_bonus[target_star],
                    )
                else:
                    improvement_stat += Stat(
                        attack_power=glove_bonus[target_star],
                    )

        mhp_data = [0, 5, 5, 5, 10, 10, 15, 15, 20, 20, 25, 25, 25, 25, 25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        mhp_types = [GearType.cap, GearType.coat, GearType.longcoat, GearType.pants, GearType.cape, GearType.ring,
                        GearType.pendant, GearType.belt, GearType.shoulder_pad, GearType.shield]
        if is_weapon:
            improvement_stat += Stat(MHP=mhp_data[target_star])
            improvement_stat += Stat(MMP=mhp_data[target_star])
        elif gear.type in mhp_types:
            improvement_stat += Stat(MHP=mhp_data[target_star])

        return improvement_stat


    def apply_superior_star(self, gear: Gear, target_star: int) -> Stat:
        if target_star >= gear.max_star:
            raise TypeError('Starforce improvement cannot exceed item constraint')

        star = target_star

        stat_data = get_starforce_increment(gear, target_star, amazing_scroll=False, att=False)
        att_data = get_starforce_increment(gear, target_star, amazing_scroll=False, att=True)

        is_weapon = gear.is_weapon() or gear.type == GearType.katara

        if gear.superior_eqp:
            for prop_type in (StatProps.STR, StatProps.DEX, StatProps.INT, StatProps.LUK):
                gear.star_stat[prop_type] += stat_data[star]
            for att_type in (StatProps.att, StatProps.matt):
                gear.star_stat[att_type] += att_data[star]
            # pdd = (gear.base_stat[StatProps.incPDD] +
            #        gear.scroll_stat[StatProps.incPDD] +
            #        gear.star_stat[StatProps.incPDD])
            # gear.star_stat[StatProps.incPDD] += pdd // 20 + 1
        else:
            stat_bonus = (2 if star > 5 else 1) if bonus and Gear.is_accessory(gear.type) else 0
            for prop_type in (StatProps.STR, StatProps.DEX, StatProps.INT, StatProps.LUK):
                if (gear.base_stat[prop_type] +
                        gear.additional_stat[prop_type] +
                        gear.scroll_stat[prop_type] +
                        gear.star_stat[prop_type] > 0):
                    gear.star_stat[prop_type] += stat_data[star] + stat_bonus

            att_bonus = 1 if bonus and (is_weapon or gear.type == GearType.shield) else 0
            for att_type in (StatProps.att, StatProps.matt):
                att = (gear.base_stat[att_type] +
                       gear.additional_stat[att_type] +
                       gear.scroll_stat[att_type] +
                       gear.star_stat[att_type])
                if att > 0:
                    gear.star_stat[att_type] += att_data[star] + att_bonus
                    if is_weapon:
                        gear.star_stat[att_type] += att // 50 + 1
            # pdd = (gear.base_stat[StatProps.incPDD] +
            #        gear.additional_stat[StatProps.incPDD] +
            #        gear.scroll_stat[StatProps.incPDD] +
            #        gear.star_stat[StatProps.incPDD])
            # gear.star_stat[StatProps.incPDD] += pdd // 20 + 1
            # if bonus and Gear.is_armor(gear.type):
            #     gear.star_stat[StatProps.incPDD] += 50
            gear.amazing_scroll = True
