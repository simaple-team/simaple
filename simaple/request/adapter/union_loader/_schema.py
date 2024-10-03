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
    block_level: str
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


class _UnionArtifactEffect(TypedDict):
    name: str
    level: int


class _UnionArtifactCrystal(TypedDict):
    name: str
    validity_flag: str
    date_expire: str
    level: int
    crystal_option_name_1: str
    crystal_option_name_2: str
    crystal_option_name_3: str


class UnionArtifactResponse(TypedDict):
    date: str
    union_artifact_effect: list[_UnionArtifactEffect]
    union_artifact_crystal: list[_UnionArtifactCrystal]
    union_artifact_remain_ap: int
