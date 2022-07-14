import math
from typing import Literal, Tuple, Union, List

from simaple.core import Stat, StatProps
from simaple.gear.bonus_factory import BonusFactory, BonusType
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository
from simaple.gear.gear_type import GearType
from simaple.gear.improvements.starforce import Starforce
from simaple.gear.improvements.spell_trace import SpellTrace, PROBABILITIES
from simaple.gear.compute.base import GearImprovementCalculator


class ScrollStarforceImprovementCalculator(GearImprovementCalculator):

    def compute(self, enhance_stat: Stat, gear: Gear, scroll_up: int, star: int) -> Tuple[Union[List[SpellTrace], Stat], Starforce]:
        """
        특정 주흔작이면 (SpellTrace list, Starforce), 주흔작으로 판별하지 못하면 (stat, Starforce)
        :param enhance_stat: Stat object of gear's scroll + star stat
        :param gear: Gear
        :param scroll_up: Gear's success scroll count
        :param star: Gear's star
        :return:
        """
        # 아직 슈페리얼 장비는 고려 안함
        starforce = Starforce(star=star)
        star_stat = starforce.calculate_improvement(gear)
        scroll_stat = Stat()
        scroll_stat.STR -= enhance_stat.STR - star_stat.STR
        scroll_stat.DEX -= enhance_stat.DEX - star_stat.DEX
        scroll_stat.INT -= enhance_stat.INT - star_stat.INT
        scroll_stat.LUK -= enhance_stat.LUK - star_stat.LUK
        scroll_stat.MHP -= enhance_stat.MHP - star_stat.MHP
        scroll_stat.MMP -= enhance_stat.MMP - star_stat.MMP
        scroll_stat.attack_power -= enhance_stat.attack_power - star_stat.attack_power
        scroll_stat.magic_attack -= enhance_stat.magic_attack - star_stat.magic_attack

        # 주스탯 찾기
        stat_type = StatProps.STR
        value = scroll_stat.STR
        if scroll_stat.DEX > value:
            value = scroll_stat.DEX
            stat_type = StatProps.DEX
        if scroll_stat.INT > value:
            value = scroll_stat.INT
            stat_type = StatProps.INT
        if scroll_stat.LUK > value:
            value = scroll_stat.LUK
            stat_type = StatProps.LUK
        if scroll_stat.MHP / 50 > value:
            value = scroll_stat.MHP
            stat_type = StatProps.MHP
        # # 올스탯 주흔작 미구현

        probs = PROBABILITIES if (gear.is_weapon() or gear.type == GearType.katara) else PROBABILITIES[:-1]

        # 동일한 주흔작만 사용했을 경우
        for prob in probs:
            st_stat = Stat()
            st_list = []
            for i in range(0, scroll_up):
                st = SpellTrace(probability=prob, stat_prop_type=stat_type, order=i + 1)
                st_list.append(st)
                st_stat += st.calculate_improvement(gear)
            if st_stat == scroll_stat:
                return st_list, starforce

        # 100%, 70%, 30% 섞작일 경우
        counts_list = []
        if len(probs) == 3:
            counts_list = self.split_number_3(scroll_up)
        elif len(probs) == 4:
            counts_list = self.split_number_4(scroll_up)

        for counts in counts_list:
            st_stat = Stat()
            st_list = []
            order = 0
            for index, prob in enumerate(probs):
                for _ in range(0, counts[index]):
                    order += 1
                    st = SpellTrace(probability=prob, stat_prop_type=stat_type, order=order)
                    st_list.append(st)
                    st_stat += st.calculate_improvement(gear)
            if st_stat == scroll_stat:
                return st_list, starforce

        # 다른 나쁜 조합들
        # 모든 조합을 tree로 나타내서 DFS 검색 ?

        return scroll_stat, starforce

    def split_number_3(self, number: int) -> (int, int, int):
        for x0 in range(0, number + 1):
            left0 = number - x0
            for x1 in range(0, left0 + 1):
                x2 = left0 - x1
                yield x0, x1, x2

    def split_number_4(self, number: int) -> (int, int, int, int):
        for x0 in range(0, number + 1):
            left0 = number - x0
            for x1 in range(0, left0 + 1):
                left1 = left0 - x1
                for x2 in range(0, left1 + 1):
                    x3 = left1 - x2
                    yield x0, x1, x2, x3
