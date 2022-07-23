import re
from abc import ABCMeta, abstractmethod
from typing import Dict, Tuple

from pydantic import BaseModel

from simaple.fetch.element.item.fragment import ItemFragment
from simaple.fetch.element.item.namespace import StatType


class DomElementProvider(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Dict[str, int]]:
        ...


class StatKeywordProvider(DomElementProvider):
    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Dict[str, int]]:
        sum_, base, bonus, increment = self._get_value(fragment)
        return {
            StatType.sum: {fragment.name: sum_},
            StatType.base: {fragment.name: base},
            StatType.bonus: {fragment.name: bonus},
            StatType.increment: {fragment.name: increment},
        }

    def _get_value(self, fragment: ItemFragment) -> Tuple[int, int, int]:
        upgradable = re.compile(r"\+([0-9]+) \(([0-9]+) \+ ([0-9]+) \+ ([0-9]+)\)")
        match = upgradable.match(fragment.text)
        if match is not None:
            return (
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                int(match.group(4)),
            )

        static = re.compile(r"\+([0-9]+)")
        match = static.match(fragment.text)
        return int(match.group(1)), int(match.group(1)), 0, 0


class MultiplierProvider(DomElementProvider):
    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Dict[str, int]]:
        sum_, base, bonus, increment = self._get_value(fragment)
        return {
            StatType.sum: {fragment.name: sum_},
            StatType.base: {fragment.name: base},
            StatType.bonus: {fragment.name: bonus},
            StatType.increment: {fragment.name: increment},
        }

    def _get_value(self, fragment: ItemFragment) -> Tuple[int, int, int]:
        upgradable = re.compile(r"\+([0-9]+)% \(([0-9]+)% \+ ([0-9]+)%\)")
        match = upgradable.match(fragment.text)
        if match is not None:
            return int(match.group(1)), int(match.group(2)), int(match.group(3)), 0

        static = re.compile(r"\+([0-9]+)%")
        match = static.match(fragment.text)
        return int(match.group(1)), int(match.group(1)), 0, 0


class PotentialProvider(DomElementProvider):
    type: StatType

    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Dict[str, int]]:
        valid_elements = fragment.children_text
        result = {}
        for idx, el in enumerate(valid_elements):
            result[idx] = self.parse_potential(el)

        return {self.type: result}

    def parse_potential(self, target: str):
        target = target.strip().replace(" ", "")
        return (
            self.match_mutiplier(target)
            or self.match_simple(target)
            or self.no_match(target)
        )

    def match_simple(self, target):
        simple_regex = re.compile(r"(.+):\+([0-9]+)")
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
    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Dict[str, int]]:
        starforce = self._get_starforce(fragment)
        return {StatType.starforce: starforce}

    def _get_starforce(self, fragment: ItemFragment) -> int:
        regex = re.compile("([0-9]+)성 강화 적용")
        match = re.search(regex, fragment.text)

        if not match:
            return 0

        return int(match.group(1))


class SoulWeaponProvider(DomElementProvider):
    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Dict[str, int]]:
        return {
            StatType.soulweapon: {
                "name": self.get_soul_name(fragment),
                "option": self.get_option(fragment),
            }
        }

    def get_soul_name(self, fragment: ItemFragment):
        regex = re.compile("^(.+) 적용")
        match = re.search(regex, fragment.text)

        return match.group(1)

    def get_option(self, fragment: ItemFragment):
        soul_option_element = fragment.children_text[0]

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
