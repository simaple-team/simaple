import re
from abc import ABCMeta, abstractmethod
from typing import Dict, Tuple

import bs4
from pydantic import BaseModel

from simaple.fetch.element.namespace import StatType


class DomElementProvider(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def get_value(self, name: str, value_element) -> Dict[StatType, Dict[str, int]]:
        ...


class StatKeywordProvider(DomElementProvider):
    def get_value(self, name, value_element) -> Dict[StatType, Dict[str, int]]:
        sum_, base, bonus, increment = self._get_value(value_element)
        return {
            StatType.sum: {name: sum_},
            StatType.base: {name: base},
            StatType.bonus: {name: bonus},
            StatType.increment: {name: increment},
        }

    def _get_value(self, value_element) -> Tuple[int, int, int]:
        upgradable = re.compile(r"\+([0-9]+) \(([0-9]+) \+ ([0-9]+) \+ ([0-9]+)\)")
        match = upgradable.match(value_element.text)
        if match is not None:
            return (
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                int(match.group(4)),
            )

        static = re.compile(r"\+([0-9]+)")
        match = static.match(value_element.text)
        return int(match.group(1)), int(match.group(1)), 0, 0


class MultiplierProvider(DomElementProvider):
    def get_value(self, name, value_element) -> Dict[StatType, Dict[str, int]]:
        sum_, base, bonus, increment = self._get_value(value_element)
        return {
            StatType.sum: {name: sum_},
            StatType.base: {name: base},
            StatType.bonus: {name: bonus},
            StatType.increment: {name: increment},
        }

    def _get_value(self, value_element) -> Tuple[int, int, int]:
        upgradable = re.compile(r"\+([0-9]+)% \(([0-9]+)% \+ ([0-9]+)%\)")
        match = upgradable.match(value_element.text)
        if match is not None:
            return int(match.group(1)), int(match.group(2)), int(match.group(3)), 0

        static = re.compile(r"\+([0-9]+)%")
        match = static.match(value_element.text)
        return int(match.group(1)), int(match.group(1)), 0, 0


class PotentialProvider(DomElementProvider):
    type: StatType

    def get_value(self, name, value_element) -> Dict[StatType, Dict[str, int]]:
        valid_elements = [
            el
            for el in value_element.children
            if isinstance(el, bs4.element.NavigableString)
        ]
        result = {}
        for el in valid_elements:
            result.update(self.parse_potential(el))

        return {self.type: result}

    def parse_potential(self, target: str):
        target = target.strip().replace(" ", "")
        return (
            self.match_simple(target)
            or self.match_mutiplier(target)
            or self.no_match(target)
        )

    def match_simple(self, target):
        simple_regex = re.compile(r"(.+):\+([0-9]+)^")
        match = simple_regex.match(target)
        if match is None:
            return None

        return {match.group(1): int(match.group(2))}

    def match_mutiplier(self, target):
        multiplier_regex = re.compile(r"(.+):\+([0-9]+)%")
        match = multiplier_regex.match(target)
        if match is None:
            return None

        return {match.group(1) + "%": int(match.group(2))}

    def no_match(self, target):
        return {target: None}


class StarforceProvider(DomElementProvider):
    def get_value(self, name: str, value_element) -> Dict[StatType, Dict[str, int]]:
        starforce = self._get_starforce(value_element)
        return {StatType.starforce: starforce}

    def _get_starforce(self, value_element) -> int:
        regex = re.compile("([0-9]+)성 강화 적용")
        match = re.search(regex, value_element.text)

        if not match:
            return 0

        return int(match.group(1))


class SoulWeaponProvider(DomElementProvider):
    def get_value(self, name: str, value_element) -> Dict[StatType, Dict[str, int]]:
        return {
            StatType.soulweapon: {
                "name": self.get_name(value_element),
                "option": self.get_option(value_element),
            }
        }

    def get_name(self, value_element):
        regex = re.compile("^(.+) 적용")
        match = re.search(regex, value_element.text)

        return match.group(1)

    def get_option(self, value_element):
        soul_option_element = [
            el
            for el in value_element.children
            if isinstance(el, bs4.element.NavigableString)
        ][0]

        normal_match = re.search(
            re.compile(r"^(.+): \+([0-9])+$"), soul_option_element.text
        )
        percent_match = re.search(
            re.compile(r"^(.+): \+([0-9])+%"), soul_option_element.text
        )

        if normal_match:
            keyword = normal_match.group(1).replace(" ", "")
            value = int(normal_match.group(2))
        elif percent_match:
            keyword = percent_match.group(1).replace(" ", "") + "%"
            value = int(percent_match.group(2))
        else:
            raise ValueError("Parsing soul option failed.")

        return {keyword: value}


class GlobalProvider(DomElementProvider):
    def get_value(self, name: str, value_element) -> Dict[StatType, Dict[str, int]]:
        return {
            StatType.name: self.get_name(value_element),
            StatType.image: self.get_image(value_element),
        }

    def get_image(self, value_element) -> str:
        image_url = value_element.find(class_="item_img").find("img")["src"]

        return image_url

    def get_name(self, value_element) -> str:
        text = value_element.find(class_="item_img").find("img")["alt"]

        improved_regex = re.compile(r"(.+)\(\+[0-9]\)")
        if improved_regex.match(text):
            return improved_regex.match(text).group(1).strip()

        return text