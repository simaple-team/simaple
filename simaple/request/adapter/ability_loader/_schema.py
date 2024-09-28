from typing import TypedDict


class _CharacterAbilityLineResponse(TypedDict):
    ability_no: str
    ability_grade: str
    ability_value: str


class CharacterAbilityResponse(TypedDict):
    date: str
    ability_grade: str
    ability_info: list[_CharacterAbilityLineResponse]
    remain_fame: float
    preset_no: int
