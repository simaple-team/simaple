from bs4 import BeautifulSoup

from simaple.fetch.element.base import Element, ElementWrapper
from simaple.fetch.query import CookiedQuery


class MapleGearsetElement(Element):
    def run(self, html_text: str):
        soup = BeautifulSoup(html_text, "html.parser")

        result = {}
        result.update(self.normal_items(soup))
        result.update(self.arcane_symbols(soup))
        return result

    @classmethod
    def expected_normal_names(cls):
        # fmt: off
        return [
            "ring1", "", "cap", "", "emblem",
            "ring2", "pendant2", "face_accessory", "", "badge",
            "ring3", "pendant1", "eye_accessory", "earrings", "medal",
            "ring4", "weapon", "coat", "shoulder_pad", "subweapon",
            "pocket", "belt", "pants", "glove", "cape",
            "", "", "shoes", "android", "machine_heart"
        ]
        # fmt: on

    @classmethod
    def expected_arcane_names(cls):
        return [f"arcane_{idx}" for idx in range(6)]

    def normal_items(self, soup):
        item_elements = soup.find(class_="item_pot").find_all("li")
        item_links = [item.find("a") for item in item_elements]
        item_urls = list(
            map(lambda element: element["href"] if element else "", item_links)
        )

        return {
            name: url
            for name, url in zip(self.expected_normal_names(), item_urls)
            if len(url) > 0
        }

    def arcane_symbols(self, soup):
        item_elements = soup.find(class_="arcane_weapon_wrap").find_all("ac_pot01")
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
