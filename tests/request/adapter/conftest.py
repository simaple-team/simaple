import json
import os
from typing import Any, cast

import pytest

from simaple.request.adapter.ability_loader._schema import CharacterAbilityResponse
from simaple.request.adapter.character_basic_loader._schema import CharacterStatResponse
from simaple.request.adapter.gear_loader._schema import (
    CashItemResponse,
    CharacterItemEquipment,
    CharacterSymbolEquipment,
    PetResponse,
    SetEffectResponse,
)
from simaple.request.adapter.hyperstat_loader._schema import CharacterHyperStatResponse
from simaple.request.adapter.link_skill_loader._schema import LinkSkillResponse
from simaple.request.adapter.propensity_loader._schema import (
    CharacterPropensityResponse,
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


@pytest.fixture
def set_effect_response() -> SetEffectResponse:
    return cast(SetEffectResponse, _macro_get_response("set_effect.json"))


@pytest.fixture
def cashitem_equipment_response() -> CashItemResponse:
    return cast(CashItemResponse, _macro_get_response("cashitem_equipment.json"))


@pytest.fixture
def union_artifact_response() -> dict[str, Any]:
    return _macro_get_response("union_artifact.json")


@pytest.fixture
def character_stat_response() -> CharacterStatResponse:
    return cast(CharacterStatResponse, _macro_get_response("character_stat.json"))


@pytest.fixture
def link_skill_response() -> LinkSkillResponse:
    return cast(LinkSkillResponse, _macro_get_response("link_skill.json"))
