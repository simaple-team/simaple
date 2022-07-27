from bs4 import BeautifulSoup

from simaple.fetch.element.base import Element
from simaple.fetch.element.character.extractor import CharacterPropertyExtractor


class CharacterElement(Element):
    extractors: dict[str, CharacterPropertyExtractor]

    def run(self, html_text: str) -> dict:
        soup = BeautifulSoup(html_text, "html.parser")

        result = {}
        for name, extractor in self.extractors.items():
            result[name] = extractor.extract(soup)

        return result
