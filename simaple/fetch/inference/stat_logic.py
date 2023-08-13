from typing import Generator

from simaple.core import BaseStatType, Stat, StatProps
from simaple.core.damage import DamageLogic
from simaple.data.damage_logic import get_damage_logic
from simaple.fetch.inference.attack_logic import JobSetting
from simaple.fetch.response.character import CharacterResponse
from simaple.gear.slot_name import SlotName

StatFactor = tuple[int, int, int]  # stat, stat_multiplier, stat_fixed


def compute_setup(
    response: CharacterResponse, setting: JobSetting, authentic_force: int
):
    def _has_genesis_weapon(response: CharacterResponse) -> bool:
        return "제네시스" in response.get_item(SlotName.weapon).meta.name

    def _get_reboot_bonus(response: CharacterResponse) -> Stat:
        if response.is_reboot():
            if response.get_level() < 250:
                return Stat(final_damage_multiplier=60)

            return Stat(final_damage_multiplier=65)

        return Stat()

    damage_logic = get_damage_logic(response.get_jobtype(), 0)
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

    base_stat += damage_logic.get_best_level_based_stat(response.get_level())
    base_stat += damage_logic.get_symbol_stat(
        _get_authentic_force_increment(response.get_level(), authentic_force)
    )
    return base_stat


def _get_authentic_force_increment(level: int, authentic_force: int) -> int:
    authentic_level = authentic_force
    static_stat = 0
    if level >= 260:  # Sernium
        static_stat += 500
        authentic_level -= 10
    if level >= 265:  # Arkus
        static_stat += 500
        authentic_level -= 10
    if level >= 270:  # Odium
        static_stat += 500
        authentic_level -= 10
    if level >= 275:  # Odium
        static_stat += 500
        authentic_level -= 10
    if level >= 280:  # Odium
        static_stat += 500
        authentic_level -= 10
    if level >= 285:  # Odium
        static_stat += 500
        authentic_level -= 10

    return static_stat + authentic_level * 20


def _calculate_stat_reliability(
    reference: StatFactor,
    inferred: StatFactor,
    stat_props: BaseStatType,
) -> float:
    """
    Calculate reliability. 0 means exactly reliable.
    You can expect "1" deivation as 1/e reliable, i.e. prob that given value is exact is 1/e.
    """

    def _static_term_reliability(
        ref: int, value: int, stat_type: BaseStatType
    ) -> float:
        offsets = {
            BaseStatType.STR: 8 * 80 + 20,
            BaseStatType.DEX: 5 * 80 + 20,
            BaseStatType.INT: 8 * 80,
            BaseStatType.LUK: 5 * 80 + 20,
        }
        offset_enabled_reference = ref + offsets[stat_type]
        return abs(offset_enabled_reference - value) * 0.05

    def _base_term_reliability(ref: int, value: int) -> float:
        if value < ref:
            return 10

        return float(abs(ref - value)) * 0.01

    def _multiplier_term_reliability(ref: int, value: int) -> float:
        if ref + 10 == value:
            return 0
        if ref == value:
            return 4
        if ref + 5 == value:
            return 8

        return 12

    return (
        _base_term_reliability(reference[0], inferred[0])
        + _multiplier_term_reliability(reference[1], inferred[1])
        + _static_term_reliability(reference[2], inferred[2], stat_props)
    )


def get_candidates(
    base_factor: StatFactor, total: int
) -> Generator[StatFactor, None, None]:
    base, mult, static = base_factor

    for mult_additive in (10, 0, 5):  # Zenon link.
        margin = 0
        while True:
            static_cand = static + margin * 10
            mult_cand = int(mult + mult_additive)

            expected_product = total - static_cand
            stat_multiplier = 1 + 0.01 * mult_cand

            base_lower_bound = expected_product / stat_multiplier
            base_upper_bound = (expected_product + 1) / stat_multiplier
            if int(base_upper_bound) < base:
                break

            if int(base_lower_bound) == base_lower_bound or int(
                base_lower_bound
            ) != int(base_upper_bound):
                base_cand = int(base_upper_bound)
                yield (base_cand, mult_cand, static_cand)

            margin += 1


def _create_task(
    response: CharacterResponse, reference_stat: Stat, base_type: BaseStatType
) -> tuple[StatFactor, int]:
    base_factor = (
        reference_stat.get(StatProps(base_type.value)),
        reference_stat.get(StatProps.multiplier(base_type)),
        reference_stat.get(StatProps.static(base_type)),
    )
    total = response.get_character_base_stat()[base_type.value]

    return base_factor, total


def get_candidates_with_score(
    reference_stat: Stat, response: CharacterResponse, base_type: BaseStatType
) -> list[tuple[StatFactor, float]]:
    base_factor, total = _create_task(response, reference_stat, base_type)
    candidates = sorted(
        [
            (
                factor_candidate,
                _calculate_stat_reliability(base_factor, factor_candidate, base_type),
            )
            for factor_candidate in get_candidates(base_factor, total)
        ],
        key=lambda v: v[1],
    )

    return candidates


def _get_scoring_target(logic: DamageLogic) -> BaseStatType:
    level_based_stat = logic.get_best_level_based_stat(250)
    if level_based_stat.STR > 4:
        return BaseStatType.STR
    if level_based_stat.DEX > 4:
        return BaseStatType.DEX
    if level_based_stat.INT > 4:
        return BaseStatType.INT
    if level_based_stat.LUK > 4:
        return BaseStatType.LUK

    raise ValueError


def _factor_to_stat(factor: StatFactor, stat_type: BaseStatType) -> Stat:
    base, mult, static = factor
    return Stat.parse_obj(
        {
            StatProps(stat_type.value).value: base,
            StatProps.multiplier(stat_type).value: mult,
            StatProps.static(stat_type).value: static,
        }
    )


def predicate_stat_factor(
    response: CharacterResponse,
    setting: JobSetting,
    authentic_force: int,
    base_type: BaseStatType,
) -> list[tuple[StatFactor, float]]:
    reference_stat = compute_setup(response, setting, authentic_force)
    return get_candidates_with_score(reference_stat, response, base_type)


def predicate_stat(
    response: CharacterResponse,
    setting: JobSetting,
    authentic_force: int,
    size: int = -1,
) -> list[tuple[Stat, float]]:
    damage_logic = get_damage_logic(response.get_jobtype(), 0)
    scoring_target_type = _get_scoring_target(damage_logic)

    reference_stat = compute_setup(response, setting, authentic_force)

    all_types = [BaseStatType.STR, BaseStatType.DEX, BaseStatType.LUK, BaseStatType.INT]

    stat = Stat()
    for stat_type in all_types:
        if stat_type == scoring_target_type:
            continue

        best_factor, _ = get_candidates_with_score(
            reference_stat,
            response,
            stat_type,
        )[0]
        stat += _factor_to_stat(best_factor, stat_type)

    scoring_candidates = get_candidates_with_score(
        reference_stat,
        response,
        scoring_target_type,
    )

    return [
        (stat + _factor_to_stat(major_factor, scoring_target_type), score)
        for major_factor, score in scoring_candidates[:size]
    ]
