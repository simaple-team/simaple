import re
from abc import ABCMeta, abstractmethod

import bs4
import pydantic


class NumberString:
    @classmethod
    def number_string_to_int(cls, number_string: str) -> int:
        return int(cls.sanitize(number_string))

    @classmethod
    def is_number(cls, number_string: str) -> bool:
        return str.isdigit(cls.sanitize(number_string))

    @classmethod
    def sanitize(cls, number_string: str) -> str:
        return number_string.strip().replace(" ", "").replace(",", "").replace("%", "")


class CharacterPropertyExtractor(pydantic.BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def extract(self, soup: bs4.BeautifulSoup):
        ...

    def sanitize(self, result) -> dict:
        sanitized_result = {}
        for k, v in result.items():
            if isinstance(v, str) and NumberString.is_number(v):
                sanitized_result[k] = NumberString.number_string_to_int(v)
            else:
                sanitized_result[k] = v

        return sanitized_result


class CharacterNameExtractor(CharacterPropertyExtractor):
    def extract(self, soup):
        name_element = soup.select_one(".char_info_top .char_name span")
        name_regex = re.compile("(.+)님$")
        name = re.search(name_regex, name_element.text).group(1)

        return name


class CharacterLevelExtractor(CharacterPropertyExtractor):
    def extract(self, soup):
        level_element = soup.select_one(".char_info_top .char_info dd")
        level_regex = re.compile(r"LV\.([0-9]+)")
        level = int(level_regex.match(level_element.text).group(1))

        return level


class CharacterOverviewExtractor(CharacterPropertyExtractor):
    def extract(self, soup):
        objectives = soup.select(".tab01_con_wrap table:nth-of-type(1) tbody td")
        overview_key_list = ("world", "job", "pop", "guild", "meso", "point")

        result = {
            overview_key: entity.text
            for overview_key, entity in zip(overview_key_list, objectives)
        }
        return self.sanitize(result)


class CharacterStatExtractor(CharacterPropertyExtractor):
    def extract(self, soup):
        stat_elements = soup.select(".tab01_con_wrap table:nth-of-type(2) tr")[:-2]
        result = {}

        stat_key_matrix = (
            ("damage_factor", "MHP"),
            ("MP", "STR"),
            ("DEX", "INT"),
            ("LUK", "critical_damage"),
            ("boss_damage_multiplier", "ignored_defence"),
            ("immunity", "stance"),
            ("armor", "speed"),
            ("jump", "starforce"),
            ("honor_point", "arcaneforce"),
        )

        for stat_key_tuple, element in zip(stat_key_matrix, stat_elements):
            for stat_key, td_element in zip(stat_key_tuple, element.find_all("td")):
                result[stat_key] = td_element.text

        min_damage_factor, max_damage_factor = result.pop("damage_factor").split("~")
        result["min_damage_factor"] = min_damage_factor
        result["max_damage_factor"] = max_damage_factor

        return self.sanitize(result)


class CharacterAbilityExtractor(CharacterPropertyExtractor):
    def extract(self, soup):
        stat_elements = [
            el.text
            for el in soup.select_one(
                ".tab01_con_wrap table:nth-of-type(2) tr:nth-last-of-type(2) td span"
            ).children
            if isinstance(el, bs4.element.NavigableString)
        ]

        regexes = {
            "STR_static": re.compile(r"STR \d+ 증가"),
            "DEX_static": re.compile(r"DEX \d+ 증가"),
            "INT_static": re.compile(r"INT \d+ 증가"),
            "LUK_static": re.compile(r"LUK \d+ 증가"),
            # 방어력 \d+ 증가
            "MHP": re.compile(r"최대 HP \d+ 증가"),
            "MMP": re.compile(r"최대 MP \d+ 증가"),
            # 점프력 \d+ 증가
            # 이동속도 \d+ 증가
            "attack_power": re.compile(r"공격력 \d+ 증가"),
            "magic_attack": re.compile(r"마력 \d+ 증가"),
            "critical_rate": re.compile(r"크리티컬 확률 \d+% 증가"),
            "allStat": re.compile(r"모든 능력치 \d+ 증가"),  # special case
            "attackSpeed": re.compile(r"공격 속도 \d+ 단계 증가"),
            "strToDEX": re.compile(r"AP를 직접 투자한 STR의 \d+% 만큼 DEX 증가"),
            "dexToSTR": re.compile(r"AP를 직접 투자한 DEX의 \d+% 만큼 STR 증가"),
            "intToLUK": re.compile(r"AP를 직접 투자한 INT의 \d+% 만큼 LUK 증가"),
            "lukToDEX": re.compile(r"AP를 직접 투자한 LUK의 \d+% 만큼 DEX 증가"),
            "relativeAttackPower": re.compile(
                r"\d+레벨마다 공격력 1 증가"
            ),  # TODO: need to verify
            "relativeMagicAttack": re.compile(
                r"\d+레벨마다 마력 1 증가"
            ),  # TODO: need to verify
            # 방어력 \d+% 증가
            "MHP_multiplier": re.compile(r"최대 HP \d+% 증가"),
            "MMP_multiplier": re.compile(r"최대 MP \d+% 증가"),
            "boss_damage_multiplier": re.compile(r"보스 몬스터 공격 시 데미지 \d+% 증가"),
            # 일반 몬스터 공격 시 데미지 \d+% 증가
            "abnormal_status_damage_multiplier": re.compile(
                r"상태 이상에 걸린 대상 공격 시 데미지 \d+% 증가"
            ),
            # 방어력의 \d+%만큼 데미지 고정값 증가
            "cooldown_reset_chance": re.compile(r"스킬 사용 시 \d+% 확률로 재사용 대기시간이 미적용"),
            "passiveSkill": re.compile(r"패시브 스킬 레벨 \d+ 증가"),
            "multiTarget": re.compile(r"다수 공격 스킬의 공격 대상 \d+ 증가"),
            "buff_duration": re.compile(r"버프 스킬의 지속 시간 \d+% 증가"),
            # 아이템 드롭률 \d+% 증가
            # 메소 획득량 \d+% 증가
        }

        result = {}

        for (key, patttern) in regexes.items():
            # default value of key is 0
            result[key] = 0

        for element in stat_elements:
            for (key, patttern) in regexes.items():
                searched = patttern.search(element)
                if searched:
                    result[key] += float(re.findall("\\d+", searched.group(0))[0])

        # migrate allStat to each stat
        for key in ["STR_static", "DEX_static", "INT_static", "LUK_static"]:
            result[key] += result["allStat"]
        del result["allStat"]

        return result


class CharacterHyperstatExtractor(CharacterPropertyExtractor):
    def extract(self, soup):
        """
        # STR, DEX, INT, LUK, HP%, MP%, DF/TF/PP/영력, 크확, 크뎀, 방무, 데미지, 보뎀, 일뎀, 내성, 공마, 경험치, 아케인포스
        # 스탯에는 스탯퍼 미적용
        """

        stat_elements = [
            el.text
            for el in soup.select_one(
                ".tab01_con_wrap table:nth-of-type(2) tr:nth-last-of-type(1) td span"
            ).children
            if isinstance(el, bs4.element.NavigableString)
        ]

        regexes = {
            "STR_static": re.compile(r"힘 \d+ 증가"),
            "DEX_static": re.compile(r"민첩성 \d+ 증가"),
            "INT_static": re.compile(r"지력 \d+ 증가"),
            "LUK_static": re.compile(r"운 \d+ 증가"),
            "MHP_multiplier": re.compile(r"최대 HP \d+% 증가"),
            "MMP_multiplier": re.compile(r"최대 MP \d+% 증가"),
            "DF": re.compile(r"최대 데몬 포스/타임 포스 \d+ 증가"),
            "PP": re.compile(r"최대 싸이킥 포인트 \d+ 증가"),
            "critical_rate": re.compile(r"크리티컬 확률 \d+% 증가"),
            "critical_damage": re.compile(r"크리티컬 데미지 \d+% 증가"),
            "ignored_defence": re.compile(r"방어율 무시 \d+% 증가"),
            "damage_multiplier": re.compile(r"데미지 \d+% 증가"),
            "boss_damage_multiplier": re.compile(r"보스 몬스터 공격 시 데미지 \d+% 증가"),
            "immunity": re.compile(r"상태 이상 내성 \d+ 증가"),
            "attack_power": re.compile(r"공격력과 마력 \d+ 증가"),
            "magic_attack": re.compile(r"공격력과 마력 \d+ 증가"),
            "arcaneforce": re.compile(r"아케인포스 \d+ 증가"),
        }

        result = {}

        for (key, patttern) in regexes.items():
            # default value of key is 0
            result[key] = 0
            for element in stat_elements:
                if patttern.match(element):
                    result[key] = float(re.findall("\\d+", element)[0])
                    break

        return result


class CharacterTraitExtractor(CharacterPropertyExtractor):
    def extract(self, soup):
        def extract_level(level_text: str) -> int:
            match = re.compile("^Lv. ([0-9]+)").match(level_text)
            if not match:
                return 0

            return int(match.group(1))

        return {
            element.find("h2").text: extract_level(
                element.select_one(".graph_wrap .lv").text
            )
            for element in soup.select(".tab02_con_wrap .dis_center")
        }
