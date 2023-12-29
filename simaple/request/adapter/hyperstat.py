from simaple.request.schema.character import CharacterHyperStat, HyperStatResponseColumn
from simaple.system.hyperstat import HYPERSTAT_BASIS, Hyperstat

_STAT_NAME_TO_BASIS_NAME = {
    "STR": "STR_static",
    "DEX": "DEX_static",
    "INT": "INT_static",
    "LUK": "LUK_static",
    "공격력/마력": "attacks",
    "데미지": "damage_multiplier",
    "보스 몬스터 공격 시 데미지 증가": "boss_damage_multiplier",
    "크리티컬 데미지": "critical_damage",
    "크리티컬 확률": "critical_rate",
    "방어율 무시": "ignored_defence",
}


def get_hyperstat(hyperstat_response: CharacterHyperStat):
    options = []
    levels = []

    target_preset: list[HyperStatResponseColumn] = hyperstat_response[
        f"hyper_stat_preset_{hyperstat_response['use_preset_no'] - 1}"  # type: ignore
    ]
    for column in target_preset:
        if column["stat_type"] in _STAT_NAME_TO_BASIS_NAME:
            options.append(
                HYPERSTAT_BASIS[_STAT_NAME_TO_BASIS_NAME[column["stat_type"]]]
            )
            levels.append(column["stat_level"])

    return Hyperstat(
        options=options,
        levels=levels,
    )
