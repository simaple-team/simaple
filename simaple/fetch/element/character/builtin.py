from simaple.fetch.element.base import Promise
from simaple.fetch.element.character.element import CharacterElement
from simaple.fetch.element.character.extractor import (
    CharacterAbilityExtractor,
    CharacterHyperstatExtractor,
    CharacterLevelExtractor,
    CharacterNameExtractor,
    CharacterOverviewExtractor,
    CharacterStatExtractor,
    PropensityExtractor,
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
            "propensity": PropensityExtractor(),
        }
    )


def character_promise() -> Promise:
    return Promise(
        element=standard_character_element(),
        query=CookiedQuery(),
        reserved_path="/Common/Character/Detail/123",
    )
