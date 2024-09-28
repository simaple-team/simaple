import json
import os
from typing import Any, cast

import pytest

from simaple.request.adapter.ability_loader._schema import CharacterAbilityResponse
from simaple.request.adapter.hyperstat_loader._schema import CharacterHyperStatResponse
from simaple.request.adapter.propensity_loader._schema import (
    CharacterPropensityResponse,
)
from simaple.request.adapter.gear_loader._schema import (
    CharacterItemEquipment,
    CharacterSymbolEquipment,
    PetResponse,
)
from simaple.request.adapter.union_loader._schema import CharacterUnionRaiderResponse


def _macro_get_response(file_name: str) -> dict[str, Any]:
    path = os.path.join(os.path.dirname(__file__), "resource", file_name)
    with open(path, "r", encoding="utf-8") as f:
        return cast(dict[str, Any], json.load(f))


@pytest.fixture
def character_hyper_stat_response() -> CharacterHyperStatResponse:
    return cast(CharacterHyperStatResponse, _macro_get_response("hyperstat.json"))


@pytest.fixture
def character_propensity_response() -> CharacterPropensityResponse:
    return cast(CharacterPropensityResponse, _macro_get_response("propensity.json"))


@pytest.fixture
def character_item_equipment_response() -> CharacterItemEquipment:
    return cast(CharacterItemEquipment, _macro_get_response("item_equipment.json"))


@pytest.fixture
def character_symbol_equipment_response() -> CharacterSymbolEquipment:
    return cast(CharacterSymbolEquipment, _macro_get_response("symbol_equipment.json"))


@pytest.fixture
def pet_response() -> PetResponse:
    return cast(PetResponse, _macro_get_response("pet_equipment.json"))


@pytest.fixture
def character_union_raiders_response() -> CharacterUnionRaiderResponse:
    return cast(
        CharacterUnionRaiderResponse,
        _macro_get_response("character_union_raiders.json"),
    )


@pytest.fixture
def character_ability_response() -> CharacterAbilityResponse:
    return cast(CharacterAbilityResponse, _macro_get_response("character_ability.json"))


@pytest.fixture
def character_ability_response_2() -> CharacterAbilityResponse:
    return cast(
        CharacterAbilityResponse, _macro_get_response("character_ability_2.json")
    )
