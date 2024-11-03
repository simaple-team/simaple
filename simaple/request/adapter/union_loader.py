import re

from simaple.core import ActionStat, ExtendedStat, JobType, Stat
from simaple.core.jobtype import translate_kms_name
from simaple.data.system.artifact import get_artifact_effects
from simaple.data.system.union_block import get_all_blocks
from simaple.request.external.nexon.api.character.union import (
    CharacterUnionRaiderBlock,
    CharacterUnionRaiderPreset,
    UnionArtifactResponse,
    get_character_union_raider_response,
    get_union_artifact_response,
)
from simaple.request.external.nexon.client import NexonAPIClient
from simaple.request.service.loader import UnionLoader
from simaple.request.service.util import BestStatSelector, get_best_stat_index
from simaple.system.artifact import Artifact, ArtifactCard
from simaple.system.union import UnionSquad


class NexonAPIUnionLoader(UnionLoader):
    def __init__(self, client: NexonAPIClient):
        self._client = client

    def load_union_squad(self, character_name: str) -> UnionSquad:
        resp = self._client.session(character_name).request(
            get_character_union_raider_response
        )
        return _get_union_squad(resp)

    def load_union_squad_effect(self, character_name: str) -> ExtendedStat:
        resp = self._client.session(character_name).request(
            get_character_union_raider_response
        )
        return _get_union_squad_effect(resp)

    def load_union_artifact(self, character_name: str) -> Artifact:
        resp = self._client.session(character_name).request(get_union_artifact_response)
        return _get_union_artifact(resp)

    def load_union_occupation_stat(self, character_name: str) -> ExtendedStat:
        resp = self._client.session(character_name).request(
            get_character_union_raider_response
        )
        return _get_occupation_stat(resp)

    def load_best_union_stat(
        self, character_name: str, selector: BestStatSelector
    ) -> ExtendedStat:
        resp = self._client.session(character_name).request(
            get_character_union_raider_response
        )
        candidates = [
            _get_occupation_stat(preset) + _get_union_squad_effect(preset)
            for preset in [
                resp["union_raider_preset_1"],
                resp["union_raider_preset_2"],
                resp["union_raider_preset_3"],
            ]
        ]

        best_candidate_index = get_best_stat_index(candidates, selector)
        return candidates[best_candidate_index]


def get_stat_from_union_raider_text(
    line: str,
) -> ExtendedStat:
    pattern = re.compile(r"^([A-Z/가-힣a-z,\s]+)([\d\.]+)(%?) (증가|감소|회복)")
    match = pattern.search(line)

    if not match:
        if rematch := re.compile(
            "공격 시 ([0-9]+)%의 확률로 데미지 ([0-9]+)% 증가"
        ).search(line):
            option_name = rematch.group(1).strip()
            option_value_float = float(rematch.group(2))
            option_value = int(option_value_float)
            return ExtendedStat(stat=Stat(damage_multiplier=option_value_float * 0.2))
        if re.compile("적 공격마다 70%의 확률로 순수 (MP|HP)의 ([0-9]+)% 회복").search(
            line
        ):
            return ExtendedStat()

        raise ValueError(f"Unknown option name: {line}")

    option_name = match.group(1).strip()
    option_value_float = float(match.group(2))
    option_value = int(option_value_float)
    is_percentage = match.group(3) == "%"

    match (option_name, is_percentage):
        case ("공격력/마력", False):
            return ExtendedStat(
                stat=Stat(attack_power=option_value, magic_attack=option_value)
            )
        case ("STR", False):
            return ExtendedStat(stat=Stat(STR_static=option_value))
        case ("DEX", False):
            return ExtendedStat(stat=Stat(DEX_static=option_value))
        case ("INT", False):
            return ExtendedStat(stat=Stat(INT_static=option_value))
        case ("LUK", False):
            return ExtendedStat(stat=Stat(LUK_static=option_value))
        case ("STR, DEX, LUK", False):
            return ExtendedStat(
                stat=Stat(
                    STR_static=option_value,
                    DEX_static=option_value,
                    LUK_static=option_value,
                )
            )
        case ("경험치 획득량", True):
            return ExtendedStat()
        case ("메소 획득량", True):
            return ExtendedStat()
        case ("스킬 재사용 대기시간", True):
            return ExtendedStat(action_stat=ActionStat(cooltime_reduce=option_value))
        case ("보스 몬스터 공격 시 데미지", True):
            return ExtendedStat(stat=Stat(boss_damage_multiplier=option_value_float))
        case ("버프 지속시간", True):
            return ExtendedStat(action_stat=ActionStat(buff_duration=option_value))
        case ("크리티컬 확률", True):
            return ExtendedStat(stat=Stat(critical_rate=option_value))
        case ("방어율 무시", True):
            return ExtendedStat(stat=Stat(ignored_defence=option_value))
        case ("상태 이상 내성", True):
            return ExtendedStat()
        case ("크리티컬 데미지", True):
            return ExtendedStat(stat=Stat(critical_damage=option_value_float))
        case ("최대 HP", True):
            return ExtendedStat(stat=Stat(MHP_multiplier=option_value))
        case ("최대 MP", True):
            return ExtendedStat(stat=Stat(MMP_multiplier=option_value))
        case ("최대 HP", False):
            return ExtendedStat(stat=Stat(MHP=option_value))
        case ("소환수 지속시간", True):
            return ExtendedStat(action_stat=ActionStat(summon_duration=option_value))
        case ("상태 이상 내성", False):
            return ExtendedStat()

    raise ValueError(f"Unknown option name: {option_name}")


def _get_stat_from_occupation_description(
    line: str,
) -> ExtendedStat:
    pattern = re.compile(r"([A-Z/가-힣a-z\s]+)([\d\.]+)(%?) 증가")
    match = pattern.search(line)
    if not match:
        raise ValueError(f"Invalid occupation description: {line}")

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
        case ("획득 경험치", True):
            return ExtendedStat()
        case ("상태이상 내성", True):
            return ExtendedStat()
        case ("일반 몬스터 공격 시 데미지", True):
            return ExtendedStat()
        case ("버프 지속시간", True):
            return ExtendedStat(action_stat=ActionStat(buff_duration=option_value))

    raise ValueError(f"Unknown option name: {option_name}")


def _get_block_size(level: int) -> int:
    if level <= 60:
        return 0
    if level < 100:
        return 1
    if level < 140:
        return 2
    if level < 200:
        return 3
    if level < 250:
        return 4

    return 5


def _get_maplestory_m_block_size(level: int) -> int:
    if level <= 30:
        return 0
    if level < 50:
        return 1
    if level < 70:
        return 2
    if level < 120:
        return 3

    return 4


def _parse_block(block: CharacterUnionRaiderBlock) -> tuple[JobType, int]:
    job_type = translate_kms_name(block["block_class"])
    level = int(block["block_level"])

    if job_type == JobType.virtual_maplestory_m:
        block_size = _get_maplestory_m_block_size(level)
    else:
        block_size = _get_block_size(level)

    return job_type, block_size


def _get_union_squad(raider_response: CharacterUnionRaiderPreset) -> UnionSquad:
    block_candidates = {block.job: block for block in get_all_blocks()}

    blocks, block_sizes = [], []

    for existing_block in raider_response["union_block"]:
        job_type, block_size = _parse_block(existing_block)
        blocks.append(block_candidates[job_type])
        block_sizes.append(block_size)

    return UnionSquad(block_size=block_sizes, blocks=blocks)


def _get_union_squad_effect(
    raider_response: CharacterUnionRaiderPreset,
) -> ExtendedStat:
    stat = ExtendedStat()

    for expression in raider_response["union_raider_stat"]:
        stat += get_stat_from_union_raider_text(expression)

    return stat


def _get_occupation_stat(response: CharacterUnionRaiderPreset) -> ExtendedStat:
    return sum(
        [
            _get_stat_from_occupation_description(expression)
            for expression in response["union_occupied_stat"]
        ],
        ExtendedStat(),
    )


def _get_union_artifact(
    response: UnionArtifactResponse,
) -> Artifact:
    effects = get_artifact_effects()

    cards = []

    for crystal in response["union_artifact_crystal"]:
        if crystal["validity_flag"] != "0":
            continue

        cards.append(
            ArtifactCard(
                effects=(
                    crystal["crystal_option_name_1"],
                    crystal["crystal_option_name_2"],
                    crystal["crystal_option_name_3"],
                ),
                level=crystal["level"],
            )
        )

    return Artifact(cards=cards, effects=effects)
