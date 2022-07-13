from simaple.fetch.query import CookiedQuery

from bs4 import BeautifulSoup
import re

from typing import Dict, Tuple, List
from simaple.fetch.element.base import Element
from simaple.fetch.query import NoredirectXMLQuery

from pydantic import BaseModel

from abc import ABCMeta, abstractmethod
from simaple.core.base import StatProps, Stat


class StatBuilder(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def call(self, value: int) -> Stat:
        ...

    def __call__(self, value: int) -> Stat:
        return self.call(value)


class SingleStatBuilder(StatBuilder):
    prop: StatProps

    def call(self, value):
        return Stat.parse_obj({self.prop.value: value})


class AllStatBuilder(StatBuilder):
    def call(self, value):
        return Stat.all_stat(value)


class AllStatMultiplierBuilder(StatBuilder):
    def call(self, value):
        return Stat.all_stat_multiplier(value)
