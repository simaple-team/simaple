from simaple.fetch.query import CookiedQuery

from bs4 import BeautifulSoup
import re

from typing import Dict, Tuple, List
from simaple.fetch.element.base import Element
from simaple.fetch.query import NoredirectXMLQuery

from pydantic import BaseModel

from abc import ABCMeta, abstractmethod
from simaple.core.base import StatProps, Stat

from simaple.fetch.element.stat_builder import SingleStatBuilder, AllStatBuilder, AllStatMultiplierBuilder
from simaple.fetch.element.provider import MultiplierProvider, StatKeywordProvider


class ItemElement(Element):
    def run(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        dom_elements = soup.find(class_="stet_info").find_all("li")

        for dom_element in dom_elements:
            k, v = self._extract_from_dom_element(dom_element)

    def _extract_from_dom_element(self, dom_element) -> Tuple[str, float]:
        print('------')
        name = dom_element.find(class_="stet_th").find('span').text
        value_element = dom_element.find(class_='point_td')


        print(name)

        print(value_element.text)
        print(str(value_element))

        return name, None

    @property
    def providers(self):
        return {
            "STR": (StatKeywordProvider(builder=SingleStatBuilder(prop=StatProps.STR))),
            "DEX": (StatKeywordProvider(builder=SingleStatBuilder(prop=StatProps.DEX))),
            "LUK": (StatKeywordProvider(builder=SingleStatBuilder(prop=StatProps.LUK))),
            "INT": (StatKeywordProvider(builder=SingleStatBuilder(prop=StatProps.INT))),
            "MaxHP": (StatKeywordProvider(builder=SingleStatBuilder(prop=StatProps.MHP))),
            "MaxMP": (StatKeywordProvider(builder=SingleStatBuilder(prop=StatProps.MMP))),

            "공격력": (StatKeywordProvider(builder=SingleStatBuilder(prop=StatProps.attack_power))),
            "마력": (StatKeywordProvider(builder=SingleStatBuilder(prop=StatProps.magic_attack))),

            "보스몬스터공격시데미지": (MultiplierProvider(builder=SingleStatBuilder(prop=StatProps.boss_damage_multiplier))),
            "올스탯": (MultiplierProvider(builder=AllStatMultiplierBuilder())),
        }

    def fetch(self, token, path):
        query = NoredirectXMLQuery(token=token, path=path)

        return query.get()
