from typing import TypedDict

from simaple.core import DamageLogic, ExtendedStat


class BestStatSelector(TypedDict):
    damage_logic: DamageLogic
    reference_stat: ExtendedStat


def get_best_stat_index(stats: list[ExtendedStat], selector: BestStatSelector) -> int:
    """
    Choose best-dealing stat index from given values
    """
    best_index = 0
    best_damage = 0.0
    damage_logic, reference_stat = selector["damage_logic"], selector["reference_stat"]

    for idx, extended_stat in enumerate(stats):
        damage = damage_logic.get_damage_factor(
            extended_stat.stat + reference_stat.stat
        )
        if damage > best_damage:
            best_damage = damage
            best_index = idx

    return best_index
