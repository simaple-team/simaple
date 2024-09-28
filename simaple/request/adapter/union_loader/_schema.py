from typing import TypedDict


class CharacterUnionResponse(TypedDict):
    date: str
    union_level: int
    union_grade: str


class _CharacterUnionRaiderBlockPos(TypedDict):
    x: int
    y: int


class CharacterUnionRaiderBlock(TypedDict):
    block_type: str
    block_class: str
    block_level: int
    block_control_point: _CharacterUnionRaiderBlockPos
    block_position: list[_CharacterUnionRaiderBlockPos]


class UnionInnerStatRow(TypedDict):
    """Union 내부 배치 방식"""

    stat_field_id: int
    stat_field_effect: str


class CharacterUnionRaiderResponse(TypedDict):
    date: str
    union_raider_stat: list[str]
    union_occupied_stat: list[str]
    union_block: list[CharacterUnionRaiderBlock]
    union_inner_stat: list[UnionInnerStatRow]
