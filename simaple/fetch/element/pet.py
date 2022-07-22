from bs4 import BeautifulSoup

from simaple.fetch.element.base import Element, ElementWrapper
from simaple.fetch.query import CookiedQuery


class PetListElement(Element):
    def run(self, html_text: str) -> dict[int, str]:
        print(html_text)
        soup = BeautifulSoup(html_text, "html.parser")

        class_element = soup.find(class_="pet_item_list").find_all("a")
        urls = [element["href"] for element in class_element]

        return dict(enumerate(urls))


def pet_list_promise():
    return ElementWrapper(
        element=PetListElement(),
        query=CookiedQuery(),
        reserved_path="/Common/Character/Detail/123/Pet",
    )
