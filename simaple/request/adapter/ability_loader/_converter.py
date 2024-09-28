import re

from simaple.core import ExtendedStat, StatProps
from simaple.request.adapter.translator.asset.stat_provider import (
    ActionStatProvider,
    AllStatProvider,
    StatProvider,
)


def kms_ability_provider_patterns() -> list[tuple[re.Pattern, list[StatProvider]]]:
    patterns = [
        (
            re.compile(r"^버프 스킬의 지속 시간 ([0-9]+)% 증가$"),
            [ActionStatProvider(target="buff_duration")],
        ),
        (
            re.compile(r"^보스 몬스터 공격 시 데미지 ([0-9]+)% 증가$"),
            [StatProvider(target=StatProps.boss_damage_multiplier)],
        ),
        (
            re.compile(r"^크리티컬 확률 ([0-9]+)% 증가$"),
            [StatProvider(target=StatProps.critical_rate)],
        ),
        (
            re.compile(r"^INT ([0-9]+) 증가$"),
            [StatProvider(target=StatProps.INT_static)],
        ),
        (
            re.compile(r"^LUK ([0-9]+) 증가$"),
            [StatProvider(target=StatProps.LUK_static)],
        ),
        (
            re.compile(r"^STR ([0-9]+) 증가$"),
            [StatProvider(target=StatProps.STR_static)],
        ),
        (
            re.compile(r"^DEX ([0-9]+) 증가$"),
            [StatProvider(target=StatProps.DEX_static)],
        ),
        (
            re.compile(r"^공격력 ([0-9]+) 증가$"),
            [StatProvider(target=StatProps.attack_power)],
        ),
        (
            re.compile(r"^마력 ([0-9]+) 증가$"),
            [StatProvider(target=StatProps.magic_attack)],
        ),
        (re.compile(r"^모든 능력치 ([0-9]+) 증가$"), [AllStatProvider()]),
    ]

    for first_stat in ("INT", "STR", "DEX", "LUK"):
        for second_stat in ("INT", "STR", "DEX", "LUK"):
            patterns += [
                (
                    re.compile(
                        f"^{first_stat} ([0-9]+) 증가, {second_stat} ([0-9]+) 증가$"
                    ),
                    [
                        StatProvider(target=StatProps(f"{first_stat}_static")),
                        StatProvider(target=StatProps(f"{second_stat}_static")),
                    ],
                )
            ]

    return patterns


class AbilityTranslator:
    def __init__(self):
        self._patterns = kms_ability_provider_patterns()

    def translate_expression(self, expression: str) -> ExtendedStat:
        for pattern, providers in self._patterns:
            match = pattern.match(expression)
            if match is not None:
                return sum(
                    [
                        provider.provide(int(match.group(idx) or "0"))
                        for idx, provider in enumerate(providers, start=1)
                    ],
                    ExtendedStat(),
                )

        raise ValueError(f"No pattern matched: {expression}")


_ABILITY_TRANSLATOR = AbilityTranslator()


def get_ability_stat_from_ability_text(line: str) -> ExtendedStat:
    return _ABILITY_TRANSLATOR.translate_expression(line)
