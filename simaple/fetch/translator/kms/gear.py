from simaple.core.base import StatProps
from simaple.fetch.translator.asset.stat_provider import (
    AllStatMultiplierProvider,
    AllStatProvider,
    StatProvider,
)
from simaple.fetch.translator.base import AbstractStatProvider
from simaple.fetch.translator.gear import GearStatTranslator


def kms_stat_providers() -> dict[str, AbstractStatProvider]:
    return {
        "STR": StatProvider(target=StatProps.STR),
        "DEX": StatProvider(target=StatProps.DEX),
        "LUK": StatProvider(target=StatProps.LUK),
        "INT": StatProvider(target=StatProps.INT),
        "STR%": StatProvider(target=StatProps.STR_multiplier),
        "DEX%": StatProvider(target=StatProps.DEX_multiplier),
        "LUK%": StatProvider(target=StatProps.LUK_multiplier),
        "INT%": StatProvider(target=StatProps.INT_multiplier),
        "STRF": StatProvider(target=StatProps.STR_static),
        "DEXF": StatProvider(target=StatProps.DEX_static),
        "LUKF": StatProvider(target=StatProps.LUK_static),
        "INTF": StatProvider(target=StatProps.INT_static),
        "MaxHP": StatProvider(target=StatProps.MHP),
        "MaxMP": StatProvider(target=StatProps.MMP),
        "공격력": StatProvider(target=StatProps.attack_power),
        "마력": StatProvider(target=StatProps.magic_attack),
        "보스몬스터공격시데미지": StatProvider(target=StatProps.boss_damage_multiplier),
        "보스몬스터공격시데미지%": StatProvider(target=StatProps.boss_damage_multiplier),
        "올스탯%": AllStatMultiplierProvider(),
        "올스탯": AllStatProvider(),
        "데미지": StatProvider(target=StatProps.damage_multiplier),
        "데미지%": StatProvider(target=StatProps.damage_multiplier),
        "몬스터방어력무시": StatProvider(target=StatProps.ignored_defence),
        "몬스터방어율무시": StatProvider(target=StatProps.ignored_defence),
        "크리티컬확률": StatProvider(target=StatProps.critical_rate),
        "크리티컬데미지": StatProvider(target=StatProps.critical_damage),
        "몬스터방어력무시%": StatProvider(target=StatProps.ignored_defence),
        "몬스터방어율무시%": StatProvider(target=StatProps.ignored_defence),
        "크리티컬확률%": StatProvider(target=StatProps.critical_rate),
        "크리티컬데미지%": StatProvider(target=StatProps.critical_damage),
    }


def kms_gear_stat_translator() -> GearStatTranslator:
    return GearStatTranslator(patterns=kms_stat_providers())
