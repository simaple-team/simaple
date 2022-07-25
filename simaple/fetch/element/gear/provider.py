import re
from abc import ABCMeta, abstractmethod
from typing import Any, Dict, Tuple

from pydantic import BaseModel

from simaple.fetch.element.gear.fragment import ItemFragment
from simaple.fetch.element.gear.namespace import StatType


class DomElementProvider(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Any]:
        ...


class StatKeywordProvider(DomElementProvider):
    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Any]:
        sum_, base, bonus, increment = self._get_value(fragment)
        return {
            StatType.sum: {fragment.name: sum_},
            StatType.base: {fragment.name: base},
            StatType.bonus: {fragment.name: bonus},
            StatType.increment: {fragment.name: increment},
        }

    def _get_value(self, fragment: ItemFragment) -> Tuple[int, int, int, int]:
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
        if match is None:
            raise ValueError("Inappropriate value parsing attempted")

        return int(match.group(1)), int(match.group(1)), 0, 0


class MultiplierProvider(DomElementProvider):
    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Any]:
        sum_, base, bonus, increment = self._get_value(fragment)
        return {
            StatType.sum: {fragment.name: sum_},
            StatType.base: {fragment.name: base},
            StatType.bonus: {fragment.name: bonus},
            StatType.increment: {fragment.name: increment},
        }

    def _get_value(self, fragment: ItemFragment) -> Tuple[int, int, int, int]:
        upgradable = re.compile(r"\+([0-9]+)% \(([0-9]+)% \+ ([0-9]+)%\)")
        match = upgradable.match(fragment.text)
        if match is not None:
            return int(match.group(1)), int(match.group(2)), int(match.group(3)), 0

        static = re.compile(r"\+([0-9]+)%")
        match = static.match(fragment.text)
        if match is None:
            raise ValueError("Inappropriate value parsing attempted")

        return int(match.group(1)), int(match.group(1)), 0, 0


class PotentialProvider(DomElementProvider):
    type: StatType

    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Any]:
        valid_elements = fragment.children_text
        options = [self.parse_potential(el) for el in valid_elements]

        return {
            self.type: {
                "option": options,
                "raw": valid_elements,
                "grade": self.get_grade(fragment.name),
            }
        }

    def get_grade(self, name: str):
        option_regex = re.compile(r"\((.+)아이템\)")
        match = re.search(option_regex, name)

        if match is None:
            return "미감정"

        return match.group(1)

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
    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Any]:
        starforce = self._get_starforce(fragment)
        return {
            StatType.starforce: starforce,
            StatType.surprise: self._detect_surprise_starforce(fragment),
        }

    def _get_starforce(self, fragment: ItemFragment) -> int:
        regex = re.compile("([0-9]+)성 강화 적용")
        match = re.search(regex, fragment.text)

        if not match:
            return 0

        return int(match.group(1))

    def _detect_surprise_starforce(self, fragment: ItemFragment) -> int:
        regex = re.compile("놀라운 장비강화 주문서가 사용되었습니다.")
        match = re.search(regex, fragment.text)

        return bool(match)


class SoulWeaponProvider(DomElementProvider):
    def get_value(self, fragment: ItemFragment) -> Dict[StatType, Any]:
        return {
            StatType.soulweapon: {
                "name": self.get_soul_name(fragment),
                "option": self.get_option(fragment),
            }
        }

    def get_soul_name(self, fragment: ItemFragment):
        regex = re.compile("^(.+) 적용")
        match = re.search(regex, fragment.text)
        if not match:
            return "소울 없음"

        return match.group(1)

    def get_option(self, fragment: ItemFragment):
        soul_option_element = fragment.children_text[0]

        normal_match = re.search(
            re.compile(r"^(.+): \+([0-9])+$"), soul_option_element.text
        )
        percent_match = re.search(
            re.compile(r"^(.+): \+([0-9])+%$"), soul_option_element.text
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
