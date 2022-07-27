from simaple.fetch.element.base import ElementWrapper
from simaple.fetch.element.character.element import CharacterElement
from simaple.fetch.element.character.extractor import (
    CharacterAbilityExtractor,
    CharacterHyperstatExtractor,
    CharacterLevelExtractor,
    CharacterNameExtractor,
    CharacterOverviewExtractor,
    CharacterStatExtractor,
    CharacterTraitExtractor,
)
from simaple.fetch.query import CookiedQuery


def standard_character_element() -> CharacterElement:
    return CharacterElement(
        extractors={
            "name": CharacterNameExtractor(),
            "level": CharacterLevelExtractor(),
            "overview": CharacterOverviewExtractor(),
            "stat": CharacterStatExtractor(),
            "ability": CharacterAbilityExtractor(),
            "hyperstat": CharacterHyperstatExtractor(),
            "trait": CharacterTraitExtractor(),
        }
    )


def character_promise() -> ElementWrapper:
    return ElementWrapper(
        element=standard_character_element(),
        query=CookiedQuery(),
        reserved_path="/Common/Character/Detail/123",
    )
