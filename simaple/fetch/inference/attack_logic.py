from itertools import product
from typing import TypedDict

from simaple.core import AttackType, Stat, StatProps
from simaple.core.damage import DamageLogic
from simaple.data.damage_logic import get_damage_logic
from simaple.fetch.response.character import CharacterResponse
from simaple.gear.slot_name import SlotName

PowerFactor = tuple[int, int, int]  # damage_multiplier, attack_multpilier, attack


def _get_power_factor(reference_stat: Stat, damage_logic: DamageLogic) -> PowerFactor:
    attack_type = damage_logic.get_attack_type()
    return (
        int(reference_stat.damage_multiplier),
        int(reference_stat.get(StatProps(attack_type.value + "_multiplier"))),
        int(reference_stat.get(StatProps(attack_type.value))),
    )


def _get_damage_multiplier_candidates(
    reference_stat: Stat,
    maximum_attack_range: int,
    damage_logic: DamageLogic,
    damage_multiplier_margin: int = 100,
) -> list[tuple[int, int]]:
    """
    returns list of [damage_multiplier, attack_power_multiplier_candidate]
    """

    final_damage_multiplier = 1 + 0.01 * reference_stat.final_damage_multiplier

    fixed_multiplier = (
        damage_logic.get_base_stat_factor(reference_stat)
        * (damage_logic.attack_range_constant)
        * 0.01
    )

    valid_multipliers = []

    for idx in range(damage_multiplier_margin):
        predicated_damage_multiplier = reference_stat.damage_multiplier + idx
        if predicated_damage_multiplier < 0:
            continue

        # first predicate rest of final damage/damage multiplier is integer.
        a_lower_bound = (
            (maximum_attack_range)
            / final_damage_multiplier
            / (1 + 0.01 * predicated_damage_multiplier)
        )
        a_upper_bound = (
            (maximum_attack_range + 1)
            / final_damage_multiplier
            / (1 + 0.01 * predicated_damage_multiplier)
        )
        if int(a_lower_bound) == int(a_upper_bound):
            continue

        # now this is integer;
        value_without_multiplier = int(a_upper_bound)

        # now assert that this value follows integer approximation.

        lower_bound = (value_without_multiplier - 0.5) / fixed_multiplier
        upper_bound = (value_without_multiplier + 0.5) / fixed_multiplier

        if int(lower_bound) == int(upper_bound):
            continue

        valid_multipliers.append((int(predicated_damage_multiplier), int(upper_bound)))

    return valid_multipliers


def _get_target_multiplier(damage_logic: DamageLogic, stat: Stat):
    if damage_logic.get_attack_type() == AttackType.attack_power:
        return stat.attack_power_multiplier
    if damage_logic.get_attack_type() == AttackType.magic_attack:
        return stat.magic_attack_multiplier

    raise ValueError


def _get_attack_candidates(
    reference_stat: Stat,
    attack_power_multiplier_candidate: int,
    damage_logic: DamageLogic,
    attack_power_multiplier_margin: int = 20,
):
    candidates = []

    for attack_power_multiplier_deviation in range(attack_power_multiplier_margin):
        predicated_attack_power_multiplier = (
            _get_target_multiplier(damage_logic, reference_stat)
            + attack_power_multiplier_deviation
        )
        attack_power_lower_bound = attack_power_multiplier_candidate / (
            1 + 0.01 * predicated_attack_power_multiplier
        )
        attack_power_upper_bound = (attack_power_multiplier_candidate + 1) / (
            1 + 0.01 * predicated_attack_power_multiplier
        )

        if int(attack_power_lower_bound) == int(attack_power_upper_bound):
            continue

        predicated_attack = int(attack_power_upper_bound)

        candidates.append(
            (
                predicated_attack_power_multiplier,
                predicated_attack,
            )
        )

    return candidates


def _get_power_factor_candidates(
    reference_stat: Stat, maximum_attack_range: int, damage_logic: DamageLogic
) -> list[PowerFactor]:
    candidates = []
    for (
        predicated_damage_multiplier,
        attack_power_multiplier_candidate,
    ) in _get_damage_multiplier_candidates(
        reference_stat,
        maximum_attack_range,
        damage_logic,
    ):
        candidates += [
            (
                predicated_damage_multiplier,
                predicated_attack_power_multiplier,
                predicated_attack,
            )
            for predicated_attack_power_multiplier, predicated_attack in _get_attack_candidates(
                reference_stat, attack_power_multiplier_candidate, damage_logic
            )
        ]

    return candidates


class JobSetting(TypedDict):
    passive: Stat
    candidates: list[list[Stat]]


def reference_stat_provider(response: CharacterResponse, setting: JobSetting):
    def _get_bare_stat(stat: Stat, character_base_stat: dict[str, int]) -> Stat:
        return Stat(
            STR=character_base_stat["STR"],
            DEX=character_base_stat["DEX"],
            INT=character_base_stat["INT"],
            LUK=character_base_stat["LUK"],
            final_damage_multiplier=stat.final_damage_multiplier,
            damage_multiplier=stat.damage_multiplier,
            attack_power_multiplier=stat.attack_power_multiplier,
            attack_power=stat.attack_power,
            magic_attack=stat.magic_attack,
            magic_attack_multiplier=stat.magic_attack_multiplier,
        )

    def _has_genesis_weapon(response: CharacterResponse) -> bool:
        return "제네시스" in response.get_item(SlotName.weapon).meta.name

    def _get_reboot_bonus(response: CharacterResponse) -> Stat:
        if response.is_reboot():
            if response.get_level() < 250:
                return Stat(final_damage_multiplier=60)

            return Stat(final_damage_multiplier=65)

        return Stat()

    item_stat = response.get_all_item_stat()
    if _has_genesis_weapon(response):
        item_stat += Stat(final_damage_multiplier=10)

    hyperstat = response.get_hyperstat()
    ability_stat = response.get_ability_stat()
    passive_stat = setting["passive"]

    base_stat = (
        item_stat
        + hyperstat
        + ability_stat
        + passive_stat
        + _get_reboot_bonus(response)
    )

    for stat_combination in product(*setting["candidates"]):
        yield _get_bare_stat(
            base_stat + sum(stat_combination, Stat()),
            response.get_character_base_stat(),
        )


def _calculate_reliability(reference: PowerFactor, inferred: PowerFactor) -> float:
    """
    Calculate reliability. 0 means exactly reliable.
    You can expect "1" deivation as 1/e reliable, i.e. prob that given value is exact is 1/e.
    """

    def _damage_multiplier_deviation(ref: int, value: int) -> float:
        return float(abs(ref - value)) * 0.02

    def _attack_multiplier_deviation(ref: int, value: int) -> float:
        return float(abs(ref - value)) * 0.5

    def _attack_deviation(ref: int, value: int) -> float:
        return float(abs(ref - value)) * 0.01

    return (
        _damage_multiplier_deviation(reference[0], inferred[0])
        + _attack_multiplier_deviation(reference[1], inferred[1])
        + _attack_deviation(reference[2], inferred[2])
    )


def predicate_attack_factor(
    response: CharacterResponse, setting: JobSetting
) -> list[tuple[PowerFactor, float]]:
    power_factor_candidates = []
    damage_logic = get_damage_logic(response.get_jobtype(), 0)

    candidates_with_score = []
    for reference_stat in reference_stat_provider(response, setting):
        power_factor_candidates += _get_power_factor_candidates(
            reference_stat, response.get_maximum_attack_range(), damage_logic
        )

        reference_damage_values = _get_power_factor(reference_stat, damage_logic)

        candidates_with_score += [
            (candidate, _calculate_reliability(reference_damage_values, candidate))
            for candidate in power_factor_candidates
        ]

    return sorted(candidates_with_score, key=lambda x: x[1])


def attack_factor_to_stat(factor: PowerFactor, damage_logic: DamageLogic) -> Stat:
    damage_multiplier, attack_multpilier, attack = factor

    return Stat.parse_obj(
        {
            damage_logic.get_attack_type().value: attack,
            damage_logic.get_attack_type().value + "_multiplier": attack_multpilier,
            "damage_multiplier": damage_multiplier,
        }
    )
