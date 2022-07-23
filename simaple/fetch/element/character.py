import re

import bs4
from bs4 import BeautifulSoup

from simaple.fetch.element.base import Element, ElementWrapper
from simaple.fetch.query import CookiedQuery


class NumberString:
    @classmethod
    def english_number_to_int(cls, number_string: str) -> int:
        return int(number_string.replace(",", ""))

    @classmethod
    def percentile_number_to_int(cls, number_string: str) -> int:
        return int(number_string.replace("%", ""))

    @classmethod
    def number_string_to_int(cls, number_string: str) -> int:
        return int(cls.sanitize(number_string))

    @classmethod
    def sanitize(cls, number_string: str) -> str:
        return number_string.strip().replace(" ", "").replace(",", "").replace("%", "")

    @classmethod
    def is_number(cls, number_string: str) -> bool:
        return str.isdigit(cls.sanitize(number_string))


class CharacterElement(Element):
    def run(self, html_text: str) -> dict:
        soup = BeautifulSoup(html_text, "html.parser")

        class_element = soup.find(class_="char_info_top")

        character_overview_element = soup.find(class_="tab01_con_wrap").find_all(
            "table"
        )
        assert len(character_overview_element) == 2

        overview_element, stat_view_element = character_overview_element
        stat_element = stat_view_element.find_all("tr")[:-2]
        ability_element = stat_view_element.find_all("tr")[-2]
        hyperstat_element = stat_view_element.find_all("tr")[-1]

        trait_element = soup.find(class_="tab02_con_wrap")

        result = {}

        result.update(self.get_class_info(class_element))
        result.update(self.get_overview(overview_element))
        result.update(self.get_stat_view(stat_element))
        result.update(self.get_ability(ability_element))
        result.update(self.get_hyperstat(hyperstat_element))
        result.update(self.get_trait(trait_element))

        sanitized_result = {}
        for k, v in result.items():
            if isinstance(v, str) and NumberString.is_number(v):
                sanitized_result[k] = NumberString.number_string_to_int(v)
            else:
                sanitized_result[k] = v

        return sanitized_result

    def get_class_info(self, class_element):
        name = class_element.find(class_="char_name").find("span").text.replace("님", "")
        level_element = class_element.find(class_="char_info").find("dd")

        level_regex = re.compile(r"LV\.([0-9]+)")
        level = int(level_regex.match(level_element.text).group(1))

        return {
            "name": name,
            "level": level,
        }

    def get_overview(self, overview_element):
        objectives = overview_element.find("tbody").find_all("td")
        index = ("world", "job", "pop", "guild", "meso", "point")

        return {idx: entity.text for idx, entity in zip(index, objectives)}

    def get_stat_view(self, stat_element):
        result = {}

        index = (
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

        for index_tuple, element in zip(index, stat_element):
            for index, td_element in zip(index_tuple, element.find_all("td")):
                result[index] = td_element.text

        min_damage_factor, max_damage_factor = result.pop("damage_factor").split("~")
        result["min_damage_factor"] = min_damage_factor
        result["max_damage_factor"] = max_damage_factor

        return result

    def get_ability(self, ability_element):
        return {
            "ability": [
                el.text
                for el in ability_element.find("td").find("span").children
                if isinstance(el, bs4.element.NavigableString)
            ]
        }

    def get_hyperstat(self, hyperstat_element):
        return {
            "hyperstat": [
                el.text
                for el in hyperstat_element.find("td").find("span").children
                if isinstance(el, bs4.element.NavigableString)
            ]
        }

    def get_trait(self, trait_element):
        def extract_level(level_text: str) -> int:
            match = re.compile("^Lv. ([0-9]+)").match(level_text)
            if not match:
                return 0

            return int(match.group(1))

        return {
            "trait": {
                element.find("h2").text: extract_level(
                    element.find(class_="graph_wrap").find(class_="lv").text
                )
                for element in trait_element.find_all(class_="dis_center")
            }
        }


def character_promise():
    return ElementWrapper(
        element=CharacterElement(),
        query=CookiedQuery(),
        reserved_path="/Common/Character/Detail/123",
    )
