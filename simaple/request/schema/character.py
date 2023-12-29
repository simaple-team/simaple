from typing import Optional, TypedDict


class CharacterBasic(TypedDict):
    date: str
    character_name: str
    world_name: str
    character_gender: str
    character_class: str
    character_class_level: str
    character_level: int
    character_exp: int
    character_exp_rate: float
    character_guild_name: str
    character_image_url: str


class CharacterPopularity(TypedDict):
    date: str
    popularity: int


class HyperStatResponseColumn(TypedDict):
    stat_type: str
    stat_point: Optional[int]
    stat_level: int
    stat_increase: str


class CharacterHyperStat(TypedDict):
    date: str
    character_class: str
    use_preset_no: int
    use_available_hyper_stat: int
    hyper_stat_preset_1: list[HyperStatResponseColumn]
    hyper_stat_preset_1_remain_point: int
    hyper_stat_preset_2: list[HyperStatResponseColumn]
    hyper_stat_preset_2_remain_point: int
    hyper_stat_preset_3: list[HyperStatResponseColumn]
    hyper_stat_preset_3_remain_point: int


class CharacterPropensity(TypedDict):
    date: str
    charisma_level: int
    sensibility_level: int
    insight_level: int
    willingness_level: int
    handicraft_level: int
    charm_level: int


class CharacterUnion(TypedDict):
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


class CharacterUnionRaider(TypedDict):
    date: str
    union_raider_stat: list[str]
    union_occupied_stat: list[str]
    union_block: list[CharacterUnionRaiderBlock]
    union_inner_stat: list[UnionInnerStatRow]
