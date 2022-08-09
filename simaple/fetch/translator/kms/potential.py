import re

from simaple.core import StatProps
from simaple.fetch.translator.asset.stat_provider import (
    ActionStatProvider,
    AllStatMultiplierProvider,
    AllStatProvider,
    LevelStatProvider,
    NullStatProvider,
    StatProvider,
)
from simaple.fetch.translator.potential import AbstractStatProvider, PotentialTranslator


def kms_potential_provider_patterns() -> list[tuple[re.Pattern, AbstractStatProvider]]:
    return [
        (re.compile(r"^DEX : \+([0-9]+)$"), StatProvider(target=StatProps.DEX)),
        (
            re.compile(r"^DEX : \+([0-9]+)%$"),
            StatProvider(target=StatProps.DEX_multiplier),
        ),
        (re.compile(r"^INT : \+([0-9]+)$"), StatProvider(target=StatProps.INT)),
        (
            re.compile(r"^INT : \+([0-9]+)%$"),
            StatProvider(target=StatProps.INT_multiplier),
        ),
        (re.compile(r"^LUK : \+([0-9]+)$"), StatProvider(target=StatProps.LUK)),
        (
            re.compile(r"^LUK : \+([0-9]+)%$"),
            StatProvider(target=StatProps.LUK_multiplier),
        ),
        (re.compile(r"^STR : \+([0-9]+)$"), StatProvider(target=StatProps.STR)),
        (
            re.compile(r"^STR : \+([0-9]+)%$"),
            StatProvider(target=StatProps.STR_multiplier),
        ),
        (
            re.compile(r"^공격력 : \+([0-9]+)$"),
            StatProvider(target=StatProps.attack_power),
        ),
        (
            re.compile(r"^공격력 : \+([0-9]+)%$"),
            StatProvider(target=StatProps.attack_power_multiplier),
        ),
        (
            re.compile(r"^데미지 : \+([0-9]+)%$"),
            StatProvider(target=StatProps.damage_multiplier),
        ),
        (re.compile(r"^마력 : \+([0-9]+)$"), StatProvider(target=StatProps.magic_attack)),
        (
            re.compile(r"^마력 : \+([0-9]+)%$"),
            StatProvider(target=StatProps.magic_attack_multiplier),
        ),
        (
            re.compile(
                r"^모든 스킬의 재사용 대기시간 : -([0-9]+)초\(10초 이하는 10%감소, 5초 미만으로 감소 불가\)$"
            ),
            ActionStatProvider(target="cooltime_reduce"),
        ),
        (
            re.compile(
                r"^모든 스킬의 재사용 대기시간 : -([0-9]+)초\(10초 이하는 5%감소, 5초 미만으로 감소 불가\)$"
            ),
            ActionStatProvider(target="cooltime_reduce"),
        ),
        (
            re.compile(r"^몬스터 방어율 무시 : \+([0-9]+)%$"),
            StatProvider(target=StatProps.ignored_defence),
        ),
        (
            re.compile(r"^보스 몬스터 공격 시 데미지 : \+([0-9]+)%$"),
            StatProvider(target=StatProps.boss_damage_multiplier),
        ),
        (re.compile(r"^올스탯 : \+([0-9]+)$"), AllStatProvider()),
        (re.compile(r"^올스탯 : \+([0-9]+)%$"), AllStatMultiplierProvider()),
        (re.compile(r"^최대 HP : \+([0-9]+)$"), StatProvider(target=StatProps.MHP)),
        (
            re.compile(r"^최대 HP : \+([0-9]+)%$"),
            StatProvider(target=StatProps.MHP_multiplier),
        ),
        (re.compile(r"^최대 MP : \+([0-9]+)$"), StatProvider(target=StatProps.MMP)),
        (
            re.compile(r"^최대 MP : \+([0-9]+)%$"),
            StatProvider(target=StatProps.MMP_multiplier),
        ),
        (
            re.compile(r"^캐릭터 기준 10레벨 당 DEX : \+([0-9]+)$"),
            LevelStatProvider(target=StatProps.DEX),
        ),
        (
            re.compile(r"^캐릭터 기준 10레벨 당 INT : \+([0-9]+)$"),
            LevelStatProvider(target=StatProps.INT),
        ),
        (
            re.compile(r"^캐릭터 기준 10레벨 당 LUK : \+([0-9]+)$"),
            LevelStatProvider(target=StatProps.LUK),
        ),
        (
            re.compile(r"^캐릭터 기준 10레벨 당 STR : \+([0-9]+)$"),
            LevelStatProvider(target=StatProps.STR),
        ),
        (
            re.compile(r"^캐릭터 기준 10레벨 당 공격력 : \+([0-9]+)$"),
            LevelStatProvider(target=StatProps.attack_power),
        ),
        (
            re.compile(r"^캐릭터 기준 10레벨 당 마력 : \+([0-9]+)$"),
            LevelStatProvider(target=StatProps.magic_attack),
        ),
        # (re.compile(r"^캐릭터 기준 10레벨 당 올스탯 : \+([0-9]+)$"), None),
        # (re.compile(r"^캐릭터 기준 10레벨 당 체력 : \+([0-9]+)$"), None),
        (
            re.compile(r"^크리티컬 데미지 : \+([0-9]+)%$"),
            StatProvider(target=StatProps.critical_damage),
        ),
        (
            re.compile(r"^크리티컬 확률 : \+([0-9]+)%$"),
            StatProvider(target=StatProps.critical_rate),
        ),
        (re.compile(r"^([0-9]+)% 확률로 받은 피해의 ([0-9]+)%를 반사$"), NullStatProvider()),
        (re.compile(r"^4초 당 ([0-9]+)의 HP 회복$"), NullStatProvider()),
        (re.compile(r"^4초 당 ([0-9]+)의 MP 회복$"), NullStatProvider()),
        (re.compile(r"^<쓸만한 미스틱 도어> 스킬 사용 가능$"), NullStatProvider()),
        (re.compile(r"^<쓸만한 샤프 아이즈> 스킬 사용 가능$"), NullStatProvider()),
        (re.compile(r"^<쓸만한 어드밴스드 블레스> 스킬 사용 가능$"), NullStatProvider()),
        (re.compile(r"^<쓸만한 윈드 부스터> 스킬 사용 가능$"), NullStatProvider()),
        (re.compile(r"^<쓸만한 컴뱃 오더스> 스킬 사용 가능$"), NullStatProvider()),
        (re.compile(r"^<쓸만한 하이퍼 바디> 스킬 사용 가능$"), NullStatProvider()),
        (re.compile(r"^<쓸만한 헤이스트> 스킬 사용 가능$"), NullStatProvider()),
        (re.compile(r"^HP 회복 아이템 및 회복 스킬 효율 : \+([0-9]+)%$"), NullStatProvider()),
        (re.compile(r"^경험치 획득 : \+([0-9]+)%$"), NullStatProvider()),
        (re.compile(r"^공격 시 ([0-9]+)% 확률로 ([0-9]+)레벨 기절효과 적용$"), NullStatProvider()),
        (re.compile(r"^공격 시 ([0-9]+)% 확률로 ([0-9]+)레벨 봉인효과 적용$"), NullStatProvider()),
        (re.compile(r"^공격 시 ([0-9]+)% 확률로 ([0-9]+)레벨 빙결효과 적용$"), NullStatProvider()),
        (re.compile(r"^공격 시 ([0-9]+)% 확률로 ([0-9]+)레벨 슬로우효과 적용$"), NullStatProvider()),
        (re.compile(r"^공격 시 ([0-9]+)% 확률로 ([0-9]+)레벨 암흑효과 적용$"), NullStatProvider()),
        (re.compile(r"^공격 시 ([0-9]+)% 확률로 ([0-9]+)레벨 중독효과 적용$"), NullStatProvider()),
        (re.compile(r"^공격 시 ([0-9]+)% 확률로 ([0-9]+)의 HP 회복$"), NullStatProvider()),
        (re.compile(r"^공격 시 ([0-9]+)% 확률로 ([0-9]+)의 MP 회복$"), NullStatProvider()),
        (re.compile(r"^공격 시 ([0-9]+)% 확률로 오토스틸$"), NullStatProvider()),
        (re.compile(r"^메소 획득량 : \+([0-9]+)%$"), NullStatProvider()),
        (re.compile(r"^모든 속성 내성 : \+([0-9]+)%$"), NullStatProvider()),
        (
            re.compile(r"^모든 스킬레벨 : \+([0-9]+)\(5차 및 일부 스킬 제외,\n스킬의 마스터 레벨까지만 증가\)$"),
            NullStatProvider(),
        ),
        (re.compile(r"^모든 스킬의 MP 소모 : -([0-9]+)%$"), NullStatProvider()),
        (re.compile(r"^몬스터 처치 시 ([0-9]+)% 확률로 ([0-9]+)의 HP 회복$"), NullStatProvider()),
        (re.compile(r"^몬스터 처치 시 ([0-9]+)% 확률로 ([0-9]+)의 MP 회복$"), NullStatProvider()),
        (re.compile(r"^방어력 : \+([0-9]+)$"), NullStatProvider()),
        (re.compile(r"^방어력 : \+([0-9]+)%$"), NullStatProvider()),
        (re.compile(r"^상태 이상 내성 : \+([0-9]+)$"), NullStatProvider()),
        (re.compile(r"^아이템 드롭률 : \+([0-9]+)%$"), NullStatProvider()),
        (re.compile(r"^이동속도 : \+([0-9]+)$"), NullStatProvider()),
        (re.compile(r"^점프력 : \+([0-9]+)$"), NullStatProvider()),
        (re.compile(r"^피격 시 ([0-9]+)% 확률로 ([0-9]+)의 데미지 무시$"), NullStatProvider()),
        (re.compile(r"^피격 시 ([0-9]+)% 확률로 ([0-9]+)초간 감동을 느낀다.$"), NullStatProvider()),
        (re.compile(r"^피격 시 ([0-9]+)% 확률로 ([0-9]+)초간 격노를 느낀다.$"), NullStatProvider()),
        (re.compile(r"^피격 시 ([0-9]+)% 확률로 ([0-9]+)초간 무적$"), NullStatProvider()),
        (re.compile(r"^피격 시 ([0-9]+)% 확률로 ([0-9]+)초간 분노를 느낀다.$"), NullStatProvider()),
        (re.compile(r"^피격 시 ([0-9]+)% 확률로 ([0-9]+)초간 사랑에 빠진다.$"), NullStatProvider()),
        (re.compile(r"^피격 시 ([0-9]+)% 확률로 ([0-9]+)초간 행복을 느낀다.$"), NullStatProvider()),
        (re.compile(r"^피격 시 ([0-9]+)% 확률로 데미지의 ([0-9]+)% 무시$"), NullStatProvider()),
        (re.compile(r"^피격 후 무적시간 : \+([0-9]+)초$"), NullStatProvider()),
    ]


def kms_potential_translator() -> PotentialTranslator:
    return PotentialTranslator(patterns=kms_potential_provider_patterns())
