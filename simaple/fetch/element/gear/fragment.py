import bs4
from pydantic import BaseModel


class ItemFragment(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    html: bs4.element.Tag

    @property
    def name(self):
        return (
            self.html.select_one(".stet_th span")
            .text.strip()
            .replace("\n", "")
            .replace(" ", "")
        )

    @property
    def children_text(self):
        return [
            el
            for el in self.embedding.children
            if isinstance(el, bs4.element.NavigableString)
        ]

    @property
    def text(self):
        return self.embedding.text

    @property
    def embedding(self):
        return self.html.find(class_="point_td")
