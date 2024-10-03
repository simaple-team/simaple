from typing import TypedDict


class _CharacterAbilityLineResponse(TypedDict):
    ability_no: str
    ability_grade: str
    ability_value: str


class _AbilityPreset(TypedDict):
    ability_info: list[_CharacterAbilityLineResponse]
    ability_preset_grade: str


class CharacterAbilityResponse(TypedDict):
    date: str
    ability_grade: str
    ability_info: list[_CharacterAbilityLineResponse]
    remain_fame: float
    preset_no: int
    ability_preset_1: _AbilityPreset
    ability_preset_2: _AbilityPreset
    ability_preset_3: _AbilityPreset
