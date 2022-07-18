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
        simple_regex = re.compile(r"(.+):\+([0-9])^")
        match = simple_regex.match(target)
        if match is None:
            return None

        return {match.group(1): int(match.group(2))}

    def match_mutiplier(self, target):
        multiplier_regex = re.compile(r"(.+):\+([0-9])%")
        match = multiplier_regex.match(target)
        if match is None:
            return None

        return {match.group(1) + "%": int(match.group(2))}

    def no_match(self, target):
        return {target: None}
