import re

import bs4
from bs4 import BeautifulSoup

from simaple.fetch.element.base import Element
from simaple.fetch.element.gear.extractor import PropertyExtractor
from simaple.fetch.element.gear.fragment import ItemFragment
from simaple.fetch.element.gear.namespace import StatType


class GearElement(Element):
    extractors: list[PropertyExtractor]

    def run(self, html_text):
        soup = BeautifulSoup(html_text, "html.parser")
        dom_elements = soup.select(".stet_info li")
        fragments = [ItemFragment(html=dom_element) for dom_element in dom_elements]
        result = {
            StatType.image: self.get_image(soup),
            StatType.name: self.get_item_name(soup),
        }

        for extractor in self.extractors:
            result.update(extractor.extract(fragments))

        return {k.value: v for k, v in result.items()}

    def get_image(self, soup: BeautifulSoup) -> str:
        image_url: str = self._get_common_element(soup)["src"]

        return image_url

    def get_item_name(self, soup: BeautifulSoup) -> str:
        text: str = self._get_common_element(soup)["alt"]

        improved_regex = re.compile(r"(.+)\(\+[0-9]\)")
        match = improved_regex.match(text)
        if match:
            return match.group(1).strip()

        return text

    def _get_common_element(self, soup: BeautifulSoup) -> bs4.element.Tag:
        image_element: bs4.element.Tag = soup.select_one(".item_img img")

        return image_element
