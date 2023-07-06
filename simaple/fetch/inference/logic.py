from simaple.core import AttackType, BaseStatType, Stat, StatProps
from simaple.data.damage_logic import get_damage_logic
from simaple.fetch.inference.attack_logic import (
    JobSetting,
    attack_factor_to_stat,
    predicate_attack_factor,
    reference_stat_provider,
)
from simaple.fetch.inference.stat_logic import predicate_stat
from simaple.fetch.response.character import CharacterResponse


def _join_scored_list(
    list_a: list[tuple[Stat, int]], list_b: list[tuple[Stat, int]], size: int
) -> list[Stat]:
    full_match = []
    for a_idx, (_, a_score) in enumerate(list_a):
        for b_idx, (_, b_score) in enumerate(list_b):
            full_match.append((a_idx, b_idx, a_score + b_score))

    full_match = sorted(full_match, key=lambda x: x[-1])

    return [
        list_a[a_idx][0] + list_b[b_idx][0] for a_idx, b_idx, _ in full_match[:size]
    ]


def infer_stat(
    response: CharacterResponse,
    setting: JobSetting,
    authentic_force: int,
    size: int = -1,
) -> list[Stat]:

    predicated_stat = predicate_stat(response, setting, authentic_force, size=size)

    damage_logic = get_damage_logic(response.get_jobtype(), 0)
    attack_factors = predicate_attack_factor(response, setting)
    if size > 0:
        attack_factors = attack_factors[:size]

    predicated_attack = [
        (attack_factor_to_stat(factor, damage_logic), score)
        for factor, score in attack_factors
    ]

    return _join_scored_list(predicated_stat, predicated_attack, size)
