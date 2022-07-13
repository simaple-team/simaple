from simaple.fetch.query import CookiedQuery

from bs4 import BeautifulSoup
import re

from typing import Dict, Tuple, List
from simaple.fetch.element.base import Element
from simaple.fetch.query import NoredirectXMLQuery

from pydantic import BaseModel

from abc import ABCMeta, abstractmethod
from simaple.core.base import StatProps, Stat
from simaple.fetch.element.stat_builder import StatBuilder


class DomElementProvider(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def get_value(self, value_element) -> Dict[str, int]:
        ...

class StatKeywordProvider(DomElementProvider):
    builder: StatBuilder
    def get_value(self, value_element) -> Dict[str, int]:
        base, bonus, increment = self._get_value(value_element)
        return {
            "base": self.builder.build(base),
            "bonus": self.builder.build(bonus),
            "increment": self.builder.build(increment),
        }

    def _get_value(self, value_element) -> Tuple[int, int, int]:
        upgradable = re.compile(r"\+([0-9]+) \(([0-9]+) \+ ([0-9]+) \+ ([0-9]+)\)")
        match = upgradable.match(value_element.text)
        if match is not None:
            return match.group(2), match.group(3), match.group(4)

        static = re.compile(r"\+([0-9]+)")
        match = static.match(value_element)
        return int(match.group(1)), 0, 0


class MultiplierProvider(DomElementProvider):
    builder: StatBuilder
    def get_value(self, value_element) -> Dict[str, int]:
        base, bonus, increment = self._get_value(value_element)
        return {
            "base": self.builder.build(base),
            "bonus": self.builder.build(bonus),
            "increment": self.builder.build(increment),
        }

    def _get_value(self, value_element) -> Tuple[int, int, int]:
        upgradable = re.compile(r"\+([0-9]+)% \(([0-9]+)% \+ ([0-9]+)%\)")
        match = upgradable.match(value_element.text)
        if match is not None:
            return match.group(2), match.group(3), 0

        static = re.compile(r"\+([0-9]+)%")
        match = static.match(value_element)
        return int(match.group(1)), 0, 0


class PotentialProvider(DomElementProvider):
    def _get_value(self, value_element):
        value_element.
        ...
