from typing import Any, cast

from simaple.request.application.base import (
    HOST,
    CharacterID,
    Token,
    get_character_id_param,
)
from simaple.request.schema.item import (
    CharacterItemElement,
    CharacterItemElementOption,
    CharacterItemEquipment,
    CharacterSymbolElement,
    CharacterSymbolEquipment,
)


def _translate_into_item_element_option(
    raw: dict[str, Any]
) -> CharacterItemElementOption:
    return cast(CharacterItemElementOption, {k: int(v) for k, v in raw.items()})


def get_character_item_equipment_element(resp: dict[str, Any]) -> CharacterItemElement:

    # fmt: off
    return {
        "item_equipment_part": resp["item_equipment_part"],
        "item_equipment_slot": resp["item_equipment_slot"],
        "item_name": resp["item_name"],
        "item_icon": resp["item_icon"],
        "item_description": resp["item_description"],
        "item_shape_name": resp["item_shape_name"],
        "item_shape_icon": resp["item_shape_icon"],
        "item_gender": resp["item_gender"],

        "item_total_option": _translate_into_item_element_option(resp["item_total_option"]),
        "item_base_option": _translate_into_item_element_option(resp["item_base_option"]),

        "potential_option_grade": resp["potential_option_grade"],
        "additional_potential_option_grade": resp["additional_potential_option_grade"],
        "potential_option_1": resp["potential_option_1"],
        "potential_option_2": resp["potential_option_2"],
        "potential_option_3": resp["potential_option_3"],
        "additional_potential_option_1": resp["additional_potential_option_1"],
        "additional_potential_option_2": resp["additional_potential_option_2"],
        "additional_potential_option_3": resp["additional_potential_option_3"],
        "equipment_level_increase": int(resp["equipment_level_increase"]),

        "item_exceptional_option": _translate_into_item_element_option(resp["item_exceptional_option"]),
        "item_add_option": _translate_into_item_element_option(resp["item_add_option"]),

        "growth_exp": resp["growth_exp"],
        "growth_level": resp["growth_level"],
        "scroll_upgrade": int(resp["scroll_upgrade"]),
        "cuttable_count": int(resp["cuttable_count"]),
        "golden_hammer_flag": resp["golden_hammer_flag"],
        "scroll_resilience_count": int(resp["scroll_resilience_count"]),
        "scroll_upgradeable_count": int(resp["scroll_upgradeable_count"]),
        "soul_name": cast(str | None, resp["soul_name"]),
        "soul_option": cast(str | None, resp["soul_option"]),

        "item_etc_option": _translate_into_item_element_option(resp["item_etc_option"]),
        "starforce": int(resp["starforce"]),
        "starforce_scroll_flag": cast(str, resp["starforce_scroll_flag"]),
        "item_starforce_option": _translate_into_item_element_option(resp["item_starforce_option"]),
        "special_ring_level": int(resp["special_ring_level"]),
        "date_expire": cast(str | None, resp["date_expire"]),
    }
    # fmt: on


async def get_character_item_equipment(
    token: Token, character_id: CharacterID
) -> CharacterItemEquipment:
    uri = f"{HOST}/maplestory/v1/character/item-equipment"

    resp = await token.request(uri, get_character_id_param(character_id))

    return {
        "date": resp["date"],
        "character_gender": resp["character_gender"],
        "character_class": resp["character_class"],
        "item_equipment": [
            get_character_item_equipment_element(item)
            for item in resp["item_equipment"]
        ],
        "title": resp["title"],
        "dragon_equipment": [
            get_character_item_equipment_element(item)
            for item in resp["dragon_equipment"]
        ],
        "mechanic_equipment": [
            get_character_item_equipment_element(item)
            for item in resp["mechanic_equipment"]
        ],
    }


def _get_symbol_element(raw: dict[str, Any]) -> CharacterSymbolElement:
    return {
        "symbol_name": raw["symbol_name"],
        "symbol_icon": raw["symbol_icon"],
        "symbol_description": raw["symbol_description"],
        "symbol_force": int(raw["symbol_force"]),
        "symbol_level": int(raw["symbol_level"]),
        "symbol_str": int(raw["symbol_str"]),
        "symbol_dex": int(raw["symbol_dex"]),
        "symbol_int": int(raw["symbol_int"]),
        "symbol_luk": int(raw["symbol_luk"]),
        "symbol_hp": int(raw["symbol_hp"]),
        "symbol_growth_count": int(raw["symbol_growth_count"]),
        "symbol_require_growth_count": int(raw["symbol_require_growth_count"]),
    }


async def get_character_symbol_equipment(
    token: Token, character_id: CharacterID
) -> CharacterSymbolEquipment:
    uri = f"{HOST}/maplestory/v1/character/symbol-equipment"

    resp = await token.request(uri, get_character_id_param(character_id))
    return {
        "date": resp["date"],
        "character_class": resp["character_class"],
        "symbol": [_get_symbol_element(item) for item in resp["symbol"]],
    }


async def get_character_set_effect(
    token: Token, character_id: CharacterID
) -> CharacterItemElement:
    uri = f"{HOST}/maplestory/v1/character/set-effect"

    resp = await token.request(uri, get_character_id_param(character_id))
    return cast(CharacterItemElement, resp)
