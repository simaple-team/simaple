import bs4
from pydantic import BaseModel, ConfigDict


class ItemFragment(BaseModel):

    html: bs4.element.Tag
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def name(self) -> str:
        return str(
            self.html.select_one(".stet_th span")
            .text.strip()
            .replace("\n", "")
            .replace(" ", "")
        )

    @property
    def children_text(self) -> list[bs4.element.NavigableString]:
        return [
            el
            for el in self.embedding.children
            if isinstance(el, bs4.element.NavigableString)
        ]

    @property
    def text(self) -> str:
        return str(self.embedding.text)

    @property
    def embedding(self):
        return self.html.find(class_="point_td")
