import json
import os
from typing import Any, cast

import pytest

from simaple.request.schema.character import (
    CharacterAbility,
    CharacterHyperStat,
    CharacterPropensity,
    CharacterUnionRaider,
)
from simaple.request.schema.item import CharacterItemEquipment, CharacterSymbolEquipment


def _macro_get_response(file_name: str) -> dict[str, Any]:
    path = os.path.join(os.path.dirname(__file__), "resource", file_name)
    with open(path, "r", encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


@pytest.fixture
def character_hyper_stat_response() -> CharacterHyperStat:
    return cast(CharacterHyperStat, _macro_get_response("hyperstat.json"))


@pytest.fixture
def character_propensity_response() -> CharacterPropensity:
    return cast(CharacterPropensity, _macro_get_response("propensity.json"))


@pytest.fixture
def character_item_equipment_response() -> CharacterItemEquipment:
    return cast(CharacterItemEquipment, _macro_get_response("item_equipment.json"))


@pytest.fixture
def character_symbol_equipment_response() -> CharacterSymbolEquipment:
    return cast(CharacterSymbolEquipment, _macro_get_response("symbol_equipment.json"))


@pytest.fixture
def character_union_raiders_response() -> CharacterUnionRaider:
    return cast(
        CharacterUnionRaider, _macro_get_response("character_union_raiders.json")
    )


@pytest.fixture
def character_ability_response() -> CharacterAbility:
    return cast(CharacterAbility, _macro_get_response("character_ability.json"))


@pytest.fixture
def character_ability_response_2() -> CharacterAbility:
    return cast(CharacterAbility, _macro_get_response("character_ability_2.json"))
