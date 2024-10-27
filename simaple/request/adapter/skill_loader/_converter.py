"""
Skill 관련 정보는 다음과 같이 처리됩니다.

1. 1,2,3,4,하이퍼, 5, 6차 스킬의 패시브 효과를 해석할 때는 skill level만 가져옵니다.
이후, 해당 skill level을 통해 패시브 효과를 가져옵니다.
따라서, 대응되는 passive skill이 정의되어 있지 않다면 캐릭터 속성에 대한 해석에 실패합니다.

2. 사용중인 하이퍼 스킬 정보를 내려줍니다.

3. Component 생성을 위한 skill level 제공을 위해, 5차, 6스킬들의 레벨을 제공합니다.

4. "기타 패시브형 스킬 정보 제공" 을 위해, 0차 스킬은 스킬의 레벨과 함께 그 효과도 추정해서 해석합니다.
이 경우 다양한 스킬 효과 변경에 대응할 수 있지만, 그 반대급부로 가끔 잘못된 정보가 제공될 수 있습니다.
"""

import re

from loguru import logger

from simaple.core import ActionStat, ExtendedStat, JobType, Stat
from simaple.data.jobs.builtin import get_damage_logic, get_passive
from simaple.data.system.hexa_stat import get_all_hexa_stat_cores
from simaple.request.adapter.translator.job_name import translate_kms_name
from simaple.request.external.nexon.api.character.skill import (
    AggregatedCharacterSkillResponse,
    CharacterSkillDescription,
    CharacterSkillResponse,
    HexaStatResponse,
)
from simaple.system.hexa_stat import HexaStat, HexaStatCore


def extract_levels(response: CharacterSkillResponse) -> dict[str, int]:
    levels = {}
    for skill in response["character_skill"]:
        levels[skill["skill_name"]] = skill["skill_level"]
    return levels


def join_passive_effect_from_skill_levels(
    jobtype: JobType,
    skill_levels_under_v: dict[str, int],
    skill_levels_over_v: dict[str, int],
    passive_skill_level: int,
    character_level: int,
    weapon_pure_attack_power: int = 0,
) -> ExtendedStat:
    """
    Apply passive skill level only for v, vi skills.
    """
    combat_orders_level = int(31 in skill_levels_under_v.values())
    passive_stat = get_passive(
        jobtype,
        combat_orders_level=combat_orders_level,
        passive_skill_level=passive_skill_level,
        character_level=character_level,
        skill_levels=skill_levels_over_v,
        weapon_pure_attack_power=weapon_pure_attack_power,  # TODO
    )

    return passive_stat


def compute_passive_skill_stat(
    responses: AggregatedCharacterSkillResponse, character_level: int
) -> ExtendedStat:
    skill_levels_under_v = extract_levels(responses["response_at_0"])
    skill_levels_under_v.update(extract_levels(responses["response_at_1"]))
    skill_levels_under_v.update(extract_levels(responses["response_at_1_and_half"]))
    skill_levels_under_v.update(extract_levels(responses["response_at_2"]))
    skill_levels_under_v.update(extract_levels(responses["response_at_2_and_half"]))
    skill_levels_under_v.update(extract_levels(responses["response_at_3"]))
    skill_levels_under_v.update(extract_levels(responses["response_at_4"]))

    skill_levels_over_v = extract_levels(responses["response_at_5"])
    skill_levels_over_v.update(extract_levels(responses["response_at_6"]))

    job_type = translate_kms_name(responses["response_at_0"]["character_class"])
    passive_stat = join_passive_effect_from_skill_levels(
        job_type,
        skill_levels_under_v,
        skill_levels_over_v,
        0,
        character_level,
    )

    return passive_stat


def get_stat_from_skill_description(
    line: str,
) -> ExtendedStat:
    pattern = re.compile(r"([A-Z/가-힣a-z\s]+)([\d\.]+)(%?) 증가")
    match = pattern.search(line)
    if not match:
        logger.warning(f"Invalid occupation description: {line}")
        return ExtendedStat()

    option_name = match.group(1).strip()
    option_value_float = float(match.group(2))
    option_value = int(option_value_float)
    is_percentage = match.group(3) == "%"

    match (option_name, is_percentage):
        case ("STR", False):
            return ExtendedStat(stat=Stat(STR_static=option_value))
        case ("DEX", False):
            return ExtendedStat(stat=Stat(DEX_static=option_value))
        case ("INT", False):
            return ExtendedStat(stat=Stat(INT_static=option_value))
        case ("LUK", False):
            return ExtendedStat(stat=Stat(LUK_static=option_value))
        case ("마력", False):
            return ExtendedStat(stat=Stat(magic_attack=option_value))
        case ("공격력", False):
            return ExtendedStat(stat=Stat(attack_power=option_value))
        case ("최대 HP", False):
            return ExtendedStat(stat=Stat(MHP=option_value))
        case ("최대 MP", False):
            return ExtendedStat(stat=Stat(MMP=option_value))
        case ("크리티컬 데미지", True):
            return ExtendedStat(stat=Stat(critical_damage=option_value_float))
        case ("크리티컬 확률", True):
            return ExtendedStat(stat=Stat(critical_rate=option_value))
        case ("방어율 무시", True):
            return ExtendedStat(stat=Stat(ignored_defence=option_value))
        case ("보스 몬스터 공격 시 데미지", True):
            return ExtendedStat(stat=Stat(boss_damage_multiplier=option_value))
        case ("몬스터 방어율 무시", True):
            return ExtendedStat(stat=Stat(ignored_defence=option_value))
        case ("공격력/마력", False):
            return ExtendedStat(
                stat=Stat(attack_power=option_value, magic_attack=option_value)
            )
        case ("일반 몬스터 공격 시 데미지", True):
            return ExtendedStat()
        case ("버프 지속시간", True):
            return ExtendedStat(action_stat=ActionStat(buff_duration=option_value))
        case ("올스탯", False):
            return ExtendedStat(stat=Stat.all_stat(option_value))

    return ExtendedStat()


def _translate_if_main_stat_core(core_name: str, job_type: JobType):
    if core_name != "주력 스탯 증가":
        return core_name

    damage_logic = get_damage_logic(job_type, 0)
    base_stat_type = damage_logic.get_base_stat_type()
    return f"주력 스탯 증가({base_stat_type.value})"


def compute_hexa_stat(resp: HexaStatResponse) -> HexaStat:
    job_type = translate_kms_name(resp["character_class"])
    return HexaStat(
        core_types=get_all_hexa_stat_cores(),
        cores=[
            HexaStatCore(
                main_stat_name=_translate_if_main_stat_core(
                    core["main_stat_name"], job_type
                ),
                sub_stat_name_1=_translate_if_main_stat_core(
                    core["sub_stat_name_1"], job_type
                ),
                sub_stat_name_2=_translate_if_main_stat_core(
                    core["sub_stat_name_2"], job_type
                ),
                main_stat_level=core["main_stat_level"],
                sub_stat_level_1=core["sub_stat_level_1"],
                sub_stat_level_2=core["sub_stat_level_2"],
            )
            for core in (
                resp["character_hexa_stat_core"] + resp["character_hexa_stat_core_2"]
            )
        ],
    )


def _get_passive_skill_effect_from_description(
    skill: CharacterSkillDescription,
) -> ExtendedStat:
    """
    패시브 스킬의 설명을 분석하여 스탯을 반환합니다.
    """

    # 여축, 정축 계산
    if skill["skill_name"] in ["정령의 축복", "여제의 축복"]:
        return ExtendedStat(
            stat=Stat(
                attack_power=skill["skill_level"], magic_attack=skill["skill_level"]
            )
        )

    # 연합의 의지
    if skill["skill_name"] == "연합의 의지":
        return ExtendedStat(
            stat=Stat(
                attack_power=5,
                magic_attack=5,
                STR=5,
                DEX=5,
                INT=5,
                LUK=5,
            )
        )
    # 창조의 아이온
    if skill["skill_name"] == "파괴의 얄다바오트":
        return ExtendedStat(
            stat=Stat(
                final_damage_multiplier=10,
            )
        )

    # None skill 반환
    if skill["skill_effect"] is None:
        return ExtendedStat()

    # 펫 계열 버프 계산
    pet_skill_regex = r"^공격력 ([0-9]+), 마력 ([0-9]+)증가$"
    if match := re.compile(pet_skill_regex).match(skill["skill_effect"]):
        return ExtendedStat(
            stat=Stat(
                attack_power=int(match.group(1)),
                magic_attack=int(match.group(2)),
            )
        )

    # 보약버프류 계산
    # 보공, 방무 명시가 되어있으면 해당 계열로 판정합니다.
    event_skill_detector = {
        "보스 몬스터 공격 시",
        "방어율 무시",
        "버프 지속시간",
        "일반 몬스터",
        "폴로/프리토",
        "몬스터파크 퇴장 시",
    }
    _event_skill_count = 0
    for event in event_skill_detector:
        if event in skill["skill_effect"]:
            _event_skill_count += 1
    if len(skill["skill_effect"].split("\n")) > 2:
        _event_skill_count += 1

    if _event_skill_count >= 2:
        return sum(
            [
                get_stat_from_skill_description(line.strip())
                for line in skill["skill_effect"].split("\n")
            ],
            ExtendedStat(),
        )

    return ExtendedStat()


def get_zero_order_skill_effect(
    response: CharacterSkillResponse,
) -> tuple[ExtendedStat, bool]:
    """
    0차 스킬의 효과를 추정합니다.
    """
    _has_liberated_skill = "파괴의 얄다바오트" in [
        skill["skill_name"] for skill in response["character_skill"]
    ]

    _ignored_skill_names = []
    _skill_effect_map = {
        skill["skill_name"]: _get_passive_skill_effect_from_description(skill)
        for skill in response["character_skill"]
        if skill["skill_name"] in {"정령의 축복", "여제의 축복"}
    }

    if "정령의 축복" in _skill_effect_map and "여제의 축복" in _skill_effect_map:
        if (
            _skill_effect_map["정령의 축복"].stat.attack_power
            > _skill_effect_map["여제의 축복"].stat.attack_power
        ):
            _ignored_skill_names.append("여제의 축복")
        else:
            _ignored_skill_names.append("정령의 축복")

    return (
        sum(
            [
                _get_passive_skill_effect_from_description(skill)
                for skill in response["character_skill"]
                if skill["skill_name"] not in _ignored_skill_names
            ],
            ExtendedStat(),
        ),
        _has_liberated_skill,
    )
