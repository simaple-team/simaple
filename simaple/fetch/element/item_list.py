from bs4 import BeautifulSoup

from simaple.fetch.element.base import Element, ElementWrapper
from simaple.fetch.query import CookiedQuery


class MapleItemListElement(Element):
    def run(self, html_text: str):
        soup = BeautifulSoup(html_text, "html.parser")

        item_elements = soup.find(class_="item_pot").find_all("li")
        item_links = [item.find("a") for item in item_elements]
        item_urls = list(
            map(lambda element: element["href"] if element else "", item_links)
        )

        return {idx: url for idx, url in enumerate(item_urls) if len(url) > 0}


def maple_item_list_promise():
    return ElementWrapper(
        element=MapleItemListElement(),
        query=CookiedQuery(),
        reserved_path="/Common/Character/Detail/123/Equipment",
    )
