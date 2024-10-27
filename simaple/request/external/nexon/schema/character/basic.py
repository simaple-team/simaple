from typing import TypedDict


class CharacterBasicResponse(TypedDict):
    date: str
    character_name: str
    world_name: str
    character_gender: str
    character_class: str
    character_class_level: str
    character_level: int
    character_exp: int
    character_exp_rate: str
    character_guild_name: str
    character_image: str
    character_date_create: str
    access_flag: str
    liberation_quest_clear_flag: str


class _CharacterFinalStat(TypedDict):
    stat_name: str
    stat_value: str


class CharacterStatResponse(TypedDict):
    date: str
    character_class: str
    final_stat: list[_CharacterFinalStat]
    remain_ap: int
