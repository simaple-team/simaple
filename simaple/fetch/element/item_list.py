from simaple.fetch.query import CookiedQuery

from bs4 import BeautifulSoup

from typing import Dict
from simaple.fetch.element.base import Element
from simaple.fetch.query import CookiedQuery


class MapleItemListElement(Element):
    def run(self, html_text: str):
        soup = BeautifulSoup(html_text, 'html.parser')

        item_elements = soup.find(class_="item_pot").find_all("li")
        item_links = [item.find('a') for item in item_elements]
        item_urls = list(map(lambda element: element['href'] if element else '', item_links))

        return item_urls

    def fetch(self, token):
        query = CookiedQuery(
            path="/Common/Character/Detail/123/Equipment",
            token=token,
        )

        return query.get()
