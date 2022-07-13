import math
from typing import Literal, Tuple, Union, List

from simaple.core import Stat, StatProps
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType
from simaple.gear.improvements.starforce import Starforce
from simaple.gear.improvements.spell_trace import SpellTrace, PROBABILITIES
from simaple.gear.compute.base import GearImprovementCalculator


class ScrollStarforceCalculator(GearImprovementCalculator):

    def compute(self, stat: Stat, gear: Gear, scroll_up: int) -> Tuple[Union[List[SpellTrace], stat], Starforce]:
        """
        특정 주흔작이면 (SpellTrace list, Starforce), 주흔작으로 판별하지 못하면 (stat, Starforce)
        :param stat: Stat object of gear's scroll + star stat
        :param gear: Gear
        :param scroll_up: Gear's success scroll count
        :return:
        """
        # 아직 슈페리얼 장비는 고려 안함
        starforce = Starforce()
        starforce.star = gear.star
        star_stat = starforce.calculate_improvement(gear)

        scroll_stat: Stat = stat - star_stat
        # 주스탯 찾기
        type = StatProps.STR
        value = scroll_stat.STR
        if scroll_stat.DEX > value:
            type = StatProps.DEX
        if scroll_stat.INT > value:
            type = StatProps.INT
        if scroll_stat.LUK > value:
            type = StatProps.LUK
        if scroll_stat.MHP / 50 > value:
            type = StatProps.MHP
        # # 올스탯 주흔작 미구현

        probs = PROBABILITIES if (gear.is_weapon() or gear.type == GearType.katara) else PROBABILITIES[:-1]

        # 동일한 주흔작만 사용했을 경우
        for prob in probs:
            st_stat = Stat()
            st_list = []
            for i in range(0, scroll_up):
                st = self.get_spell_trace(prob, type, i + 1)
                st_list.append(st)
                st_stat += st.calculate_improvement(gear)
            if st_stat == scroll_stat:
                return st_list, star_stat

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
                for _ in counts[index]:
                    order += 1
                    st = self.get_spell_trace(prob, type, order)
                    st_list.append(st)
                    st_stat += st.calculate_improvement(gear)
            if st_stat == scroll_stat:
                return st_list, star_stat

        # 다른 나쁜 조합들
        # 모든 조합을 tree로 나타내서 DFS 검색 ?

        return scroll_stat, starforce

    def get_spell_trace(self, probability: int, stat_prop_type: StatProps, order: int):
        spell_trace = SpellTrace()
        spell_trace.probability = probability
        spell_trace.stat_prop_type = stat_prop_type
        spell_trace.order = order
        return spell_trace

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

