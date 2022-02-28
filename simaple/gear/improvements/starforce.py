from simaple.core.base import Stat, Ability
from pydantic import BaseModel, conint
from simaple.gear.gear_type import GearType
from simaple.gear.gear import Gear
from simaple.gear.improvements.base import GearImprovement
from typing import Literal

import enum
import math


class Starforce(BaseModel):
    type: Literal['Starforce'] = 'Starforce'
    star: int

    def max_star(self, gear: Gear) -> int:
        """
        Returns the number of gear's max star.
        :return: The number of gear's max star.
        """
        if gear.tuc <= 0:
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


    def apply_stars(self, count: int, amazing_scroll: bool = False, bonus: bool = False) -> int:
        """
        Apply multiple stars and corresponding stats.
        :param count: Number for stars to apply.
        :param amazing_scroll: True to apply blue star; False to apply yellow star.
        :param bonus: True to apply bonus stat to blue star; False otherwise.
        :return: Number of increased stars.
        :raises AttributeError: If gear is not set.
        """
        suc = 0
        for i in range(0, count):
            suc += 1 if self.apply_star(amazing_scroll, bonus) else 0
        return suc


    def apply_star(self, gear: Gear, current_star: int) -> Stat:
        """
        Apply single star and corresponding stats.
        :param amazing_scroll: True to apply blue star; False to apply yellow star.
        :param bonus: True to apply bonus stat to blue star; False otherwise.
        :return: True if applied; False otherwise.
        :raises AttributeError: If gear is not set.
        """
        if current_star >= gear.max_star:
            raise TypeError('Starforce improvement cannot exceed item constraint')

        star = current_star

        stat_data = _get_star_data(self.gear, amazing_scroll=False, att=False)
        att_data = _get_star_data(self.gear, amazing_scroll=False, att=True)

        is_weapon = gear.is_weapon() or gear.type == GearType.katara

        if self.gear.superior_eqp:
            for prop_type in (GearPropType.STR, GearPropType.DEX, GearPropType.INT, GearPropType.LUK):
                self.gear.star_stat[prop_type] += stat_data[star]
            for att_type in (GearPropType.att, GearPropType.matt):
                self.gear.star_stat[att_type] += att_data[star]
            # pdd = (self.gear.base_stat[GearPropType.incPDD] +
            #        self.gear.scroll_stat[GearPropType.incPDD] +
            #        self.gear.star_stat[GearPropType.incPDD])
            # self.gear.star_stat[GearPropType.incPDD] += pdd // 20 + 1
        elif not amazing_scroll:
            job_stat = [
                [GearPropType.STR, GearPropType.DEX],
                [GearPropType.INT, GearPropType.LUK],
                [GearPropType.DEX, GearPropType.STR],
                [GearPropType.LUK, GearPropType.DEX],
                [GearPropType.STR, GearPropType.DEX],
            ]
            stat_set: Set[GearPropType]
            req_job = self.gear.req_job
            if req_job == 0:
                stat_set = {GearPropType.STR, GearPropType.DEX, GearPropType.INT, GearPropType.LUK}
            else:
                stat_set = set()
                for i in range(0, 5):
                    if req_job & (1 << i) != 0:
                        for prop_type in job_stat[i]:
                            stat_set.add(prop_type)
            for prop_type in (GearPropType.STR, GearPropType.DEX, GearPropType.INT, GearPropType.LUK):
                if prop_type in stat_set:
                    self.gear.star_stat[prop_type] += stat_data[star]
                elif star > 15 and self.gear.base_stat[prop_type] + self.gear.scroll_stat[prop_type] > 0:
                    self.gear.star_stat[prop_type] += stat_data[star]

            if is_weapon:
                use_mad = req_job == 0 or req_job // 2 % 2 == 1 or self.gear.scroll_stat[GearPropType.matt] > 0
                if star > 15:
                    self.gear.star_stat[GearPropType.att] += att_data[star]
                    if use_mad:
                        self.gear.star_stat[GearPropType.matt] += att_data[star]
                else:
                    pad = (self.gear.base_stat[GearPropType.att] +
                           self.gear.scroll_stat[GearPropType.att] +
                           self.gear.star_stat[GearPropType.att])
                    self.gear.star_stat[GearPropType.att] += pad // 50 + 1
                    if use_mad:
                        mad = (self.gear.base_stat[GearPropType.matt] +
                               self.gear.scroll_stat[GearPropType.matt] +
                               self.gear.star_stat[GearPropType.matt])
                        self.gear.star_stat[GearPropType.matt] += mad // 50 + 1
            else:
                self.gear.star_stat[GearPropType.att] += att_data[star]
                self.gear.star_stat[GearPropType.matt] += att_data[star]
                if self.gear.type == GearType.glove:
                    glove_bonus = [0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    if req_job == 0:
                        self.gear.star_stat[GearPropType.att] += glove_bonus[star]
                        self.gear.star_stat[GearPropType.matt] += glove_bonus[star]
                    elif req_job // 2 % 2 == 1:
                        self.gear.star_stat[GearPropType.matt] += glove_bonus[star]
                    else:
                        self.gear.star_stat[GearPropType.att] += glove_bonus[star]

            if not is_weapon and self.gear.type != GearType.machine_heart:
                # pdd = (self.gear.base_stat[GearPropType.incPDD] +
                #        self.gear.scroll_stat[GearPropType.incPDD] +
                #        self.gear.star_stat[GearPropType.incPDD])
                # self.gear.star_stat[GearPropType.incPDD] += pdd // 20 + 1
                pass

            mhp_data = [0, 5, 5, 5, 10, 10, 15, 15, 20, 20, 25, 25, 25, 25, 25, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            mhp_types = [GearType.cap, GearType.coat, GearType.longcoat, GearType.pants, GearType.cape, GearType.ring,
                         GearType.pendant, GearType.belt, GearType.shoulder_pad, GearType.shield]
            if is_weapon:
                self.gear.star_stat[GearPropType.MHP] += mhp_data[star]
                self.gear.star_stat[GearPropType.MMP] += mhp_data[star]
            elif self.gear.type in mhp_types:
                self.gear.star_stat[GearPropType.MHP] += mhp_data[star]

            # if self.gear.type == GearType.shoes:
                # speed_jump_data = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                # self.gear.star_stat[GearPropType.incSpeed] += speed_jump_data[star]
                # self.gear.star_stat[GearPropType.incJump] += speed_jump_data[star]
        else:
            stat_bonus = (2 if star > 5 else 1) if bonus and Gear.is_accessory(self.gear.type) else 0
            for prop_type in (GearPropType.STR, GearPropType.DEX, GearPropType.INT, GearPropType.LUK):
                if (self.gear.base_stat[prop_type] +
                        self.gear.additional_stat[prop_type] +
                        self.gear.scroll_stat[prop_type] +
                        self.gear.star_stat[prop_type] > 0):
                    self.gear.star_stat[prop_type] += stat_data[star] + stat_bonus

            att_bonus = 1 if bonus and (is_weapon or self.gear.type == GearType.shield) else 0
            for att_type in (GearPropType.att, GearPropType.matt):
                att = (self.gear.base_stat[att_type] +
                       self.gear.additional_stat[att_type] +
                       self.gear.scroll_stat[att_type] +
                       self.gear.star_stat[att_type])
                if att > 0:
                    self.gear.star_stat[att_type] += att_data[star] + att_bonus
                    if is_weapon:
                        self.gear.star_stat[att_type] += att // 50 + 1
            # pdd = (self.gear.base_stat[GearPropType.incPDD] +
            #        self.gear.additional_stat[GearPropType.incPDD] +
            #        self.gear.scroll_stat[GearPropType.incPDD] +
            #        self.gear.star_stat[GearPropType.incPDD])
            # self.gear.star_stat[GearPropType.incPDD] += pdd // 20 + 1
            # if bonus and Gear.is_armor(self.gear.type):
            #     self.gear.star_stat[GearPropType.incPDD] += 50
            self.gear.amazing_scroll = True
        return True



def _get_star_data(gear: Gear, amazing_scroll: bool, att: bool) -> List[int]:
    if gear.superior_eqp:
        if att:
            data = __superior_att_data
        else:
            data = __superior_stat_data
    elif not amazing_scroll:
        if att:
            if Gear.is_weapon(gear.type) or gear.type == GearType.katara:
                data = __starforce_weapon_att_data
            else:
                data = __starforce_att_data
        else:
            data = __starforce_stat_data
    else:
        if att:
            data = __amazing_att_data
        else:
            data = __amazing_stat_data
    stat = None
    for item in data:
        if gear.req_level >= item[0]:
            stat = item
        else:
            break
    return stat


__superior_att_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [110, 0, 0, 0, 0, 0, 5, 6, 7, 0, 0, 0, 0, 0, 0, 0],
    [150, 0, 0, 0, 0, 0, 9, 10, 11, 12, 13, 15, 17, 19, 21, 23],
]
__superior_stat_data = [
    [0, 1, 2, 4, 7, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [80, 2, 3, 5, 8, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [110, 9, 10, 12, 15, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [150, 19, 20, 22, 25, 29, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
__starforce_weapon_att_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [108, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 5, 6, 7, 8, 9, 27, 28, 29],
    [118, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 6, 7, 8, 9, 10, 28, 29, 30],
    [128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 7, 7, 8, 9, 10, 11, 29, 30, 31],
    [138, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 8, 8, 9, 10, 11, 12, 30, 31, 32],
    [148, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 9, 10, 11, 12, 13, 31, 32, 33],
    [158, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 9, 10, 11, 12, 13, 14, 32, 33, 34],
    [198, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 13, 14, 14, 15, 16, 17, 34, 35, 36],
]
__starforce_att_data = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [108, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 9, 10, 12, 13, 15, 17],
    [118, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 7, 8, 9, 10, 11, 13, 14, 16, 18],
    [128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20],
    [138, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 9, 10, 11, 12, 13, 15, 17, 19, 21],
    [148, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22],
    [158, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 11, 12, 13, 14, 15, 17, 19, 21, 23],
    [198, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 13, 14, 15, 16, 17, 19, 21, 23, 25],
]
__starforce_stat_data = [
    [0, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [108, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0],
    [118, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 0, 0, 0],
    [128, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0],
    [138, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 9, 9, 9, 9, 9, 9, 9, 0, 0, 0],
    [148, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 11, 11, 11, 11, 11, 11, 11, 0, 0, 0],
    [158, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 13, 13, 13, 13, 13, 13, 13, 0, 0, 0],
    [198, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 15, 15, 15, 15, 15, 15, 15, 0, 0, 0],
]
__amazing_att_data = [
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
__amazing_stat_data = [
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
