from typing import TypedDict

from simaple.core import AttackType, Stat, StatProps
from simaple.core.damage import DamageLogic
from simaple.data.damage_logic import get_damage_logic
from simaple.fetch.response.character import CharacterResponse
from simaple.gear.slot_name import SlotName
from simaple.fetch.inference.logic import reference_stat_provider, JobSetting


StatFactor = tuple[int, int, int]  # stat, stat_multiplier, stat_fixed



def compute_setup(response: CharacterResponse, setting: JobSetting):
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

    for variation in setting["candidates"]:
        yield _get_bare_stat(base_stat + variation, response.get_character_base_stat())


def predicate_stat(
    response: CharacterResponse, setting: JobSetting
) -> list[StatFactor, int]:
    damage_logic = get_damage_logic(response.get_jobtype(), 0)
    major_stat = "INT"

    for reference_stat in reference_stat_provider(response, setting):
        ...
