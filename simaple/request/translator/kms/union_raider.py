import re

from simaple.core import ExtendedStat, Stat, StatProps
from simaple.request.translator.asset.stat_provider import (
    AbstractStatProvider,
    ActionStatProvider,
    AllAttackProvider,
    NullStatProvider,
    StatProvider,
)
from simaple.request.translator.base import NoMatchedStringError


class ZenonProvider(AbstractStatProvider):
    def provide(self, dependency: float) -> ExtendedStat:
        return ExtendedStat(
            stat=Stat(
                STR_static=dependency,
                DEX_static=dependency,
                LUK_static=dependency,
            )
        )


class WildHunterProvider(AbstractStatProvider):
    def provide(self, dependency: float) -> ExtendedStat:
        return ExtendedStat(
            stat=Stat(
                damage_multiplier=dependency * 0.2,
            )
        )


def kms_union_provider_patterns() -> list[tuple[re.Pattern, AbstractStatProvider]]:
    return [
        (re.compile(r"^공격력/마력 ([0-9]+) 증가$"), AllAttackProvider()),
        (re.compile(r"^STR ([0-9]+) 증가$"), StatProvider(target=StatProps.STR_static)),
        (re.compile(r"^DEX ([0-9]+) 증가$"), StatProvider(target=StatProps.DEX_static)),
        (re.compile(r"^INT ([0-9]+) 증가$"), StatProvider(target=StatProps.INT_static)),
        (re.compile(r"^LUK ([0-9]+) 증가$"), StatProvider(target=StatProps.LUK_static)),
        (re.compile(r"^STR, DEX, LUK ([0-9]+) 증가$"), ZenonProvider()),
        (
            re.compile(r"^적 공격마다 70%의 확률로 순수 HP의 ([0-9]+)% 회복$"),
            NullStatProvider(),
        ),
        (
            re.compile(r"^적 공격마다 70%의 확률로 순수 MP의 ([0-9]+)% 회복$"),
            NullStatProvider(),
        ),
        (re.compile(r"^경험치 획득량 ([0-9]+)% 증가$"), NullStatProvider()),
        (re.compile(r"^메소 획득량 ([0-9]+)% 증가$"), NullStatProvider()),
        (
            re.compile(r"^스킬 재사용 대기시간 ([0-9]+)% 감소$"),
            ActionStatProvider(target="cooltime_reduce"),
        ),
        (
            re.compile(r"^보스 몬스터 공격 시 데미지 ([0-9]+)% 증가$"),
            StatProvider(target=StatProps.boss_damage_multiplier),
        ),
        (
            re.compile(r"^버프 지속시간 ([0-9]+)% 증가$"),
            ActionStatProvider(target="buff_duration"),
        ),
        (
            re.compile(r"^크리티컬 확률 ([0-9]+)% 증가$"),
            StatProvider(target=StatProps.critical_rate),
        ),
        (
            re.compile(r"^방어율 무시 ([0-9]+)% 증가$"),
            StatProvider(target=StatProps.ignored_defence),
        ),
        (re.compile(r"^상태 이상 내성 ([0-9]+) 증가$"), NullStatProvider()),
        (
            re.compile(r"^크리티컬 데미지 ([0-9]+)% 증가$"),
            StatProvider(target=StatProps.critical_damage),
        ),
        (
            re.compile(r"^최대 HP ([0-9]+)% 증가$"),
            StatProvider(target=StatProps.MHP_multiplier),
        ),
        (
            re.compile(r"^최대 MP ([0-9]+)% 증가$"),
            StatProvider(target=StatProps.MMP_multiplier),
        ),
        (re.compile(r"^최대 HP ([0-9]+) 증가$"), StatProvider(target=StatProps.MHP)),
        (
            re.compile(r"^공격 시 20%의 확률로 데미지 ([0-9]+)% 증가$"),
            WildHunterProvider(),
        ),
    ]


class UnionStatTranslator:
    def __init__(self, patterns: list[tuple[re.Pattern, AbstractStatProvider]]):
        self.patterns = patterns

    def translate(self, expression: str) -> ExtendedStat:
        for pattern, provider in self.patterns:
            match = pattern.match(expression)
            if match:
                return provider.provide(float(match.group(1)))

        raise NoMatchedStringError(f"No pattern matched: {expression}")


def kms_union_stat_translator() -> UnionStatTranslator:
    return UnionStatTranslator(patterns=kms_union_provider_patterns())
