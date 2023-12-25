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
