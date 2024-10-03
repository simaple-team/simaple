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

from simaple.core import ExtendedStat, JobType
from simaple.data.jobs.builtin import get_passive
from simaple.request.adapter.skill_loader._schema import (
    AggregatedCharacterSkillResponse,
    CharacterSkillResponse,
)
from simaple.request.adapter.translator.job_name import translate_kms_name


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
):
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
