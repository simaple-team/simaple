from bs4 import BeautifulSoup

from simaple.fetch.element.base import Element, ElementWrapper
from simaple.fetch.query import CookiedQuery


class PetListElement(Element):
    def run(self, html_text: str) -> dict[str, str]:
        soup = BeautifulSoup(html_text, "html.parser")

        class_element = soup.select(".pet_item_list a")
        urls = [element["href"] for element in class_element]

        return {str(k): v for k, v in enumerate(urls)}


def pet_list_promise():
    return ElementWrapper(
        element=PetListElement(),
        query=CookiedQuery(),
        reserved_path="/Common/Character/Detail/123/Pet",
    )
