from typing import Optional, TypedDict


class HyperStatResponseColumnResponse(TypedDict):
    stat_type: str
    stat_point: Optional[int]
    stat_level: int
    stat_increase: str


class CharacterHyperStatResponse(TypedDict):
    date: str
    character_class: str
    use_preset_no: int
    use_available_hyper_stat: int
    hyper_stat_preset_1: list[HyperStatResponseColumnResponse]
    hyper_stat_preset_1_remain_point: int
    hyper_stat_preset_2: list[HyperStatResponseColumnResponse]
    hyper_stat_preset_2_remain_point: int
    hyper_stat_preset_3: list[HyperStatResponseColumnResponse]
    hyper_stat_preset_3_remain_point: int
