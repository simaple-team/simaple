from bs4 import BeautifulSoup

from simaple.fetch.element.base import Element, ElementWrapper
from simaple.fetch.query import CookiedQuery
from simaple.gear.slot_name import SlotName


class MapleGearsetElement(Element):
    def run(self, html_text: str):
        soup = BeautifulSoup(html_text, "html.parser")

        result = {}
        result.update(self.normal_items(soup))
        result.update(self.arcane_symbols(soup))
        result.update(self.cash_items(soup))
        return result

    @classmethod
    def expected_normal_names(cls) -> list[str]:
        return [
            slot_name.value if slot_name else ""
            for slot_name in sum(SlotName.normal_item_grid(), [])
        ]

    @classmethod
    def expected_cash_names(cls) -> list[str]:
        return [
            slot_name.value if slot_name else ""
            for slot_name in sum(SlotName.cash_item_grid(), [])
        ]

    @classmethod
    def expected_arcane_names(cls):
        return [slot_name.value for slot_name in SlotName.arcane_items()]

    def normal_items(self, soup):
        item_elements = soup.select(".tab01_con_wrap li")
        item_links = [item.find("a") for item in item_elements]
        item_urls = list(
            map(lambda element: element["href"] if element else "", item_links)
        )

        return {
            name: url
            for name, url in zip(self.expected_normal_names(), item_urls)
            if len(url) > 0
        }

    def cash_items(self, soup):
        item_elements = soup.select(".tab02_con_wrap li")
        item_links = [item.find("a") for item in item_elements]
        item_urls = list(
            map(lambda element: element["href"] if element else "", item_links)
        )

        return {
            name: url
            for name, url in zip(self.expected_cash_names(), item_urls)
            if len(url) > 0
        }

    def arcane_symbols(self, soup):
        item_elements = soup.select(".tab03_con_wrap li")
        item_links = [item.find("a") for item in item_elements]
        item_urls = list(
            map(lambda element: element["href"] if element else "", item_links)
        )

        return {
            name: url
            for name, url in zip(self.expected_arcane_names(), item_urls)
            if len(url) > 0
        }


def maple_gearset_promise():
    return ElementWrapper(
        element=MapleGearsetElement(),
        query=CookiedQuery(),
        reserved_path="/Common/Character/Detail/123/Equipment",
    )
