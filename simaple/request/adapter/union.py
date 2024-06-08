from simaple.core import ExtendedStat, JobType
from simaple.data.system.union_block import get_all_blocks
from simaple.request.schema.character import (
    CharacterUnionRaider,
    CharacterUnionRaiderBlock,
)
from simaple.request.translator.job_name import translate_kms_name
from simaple.request.translator.kms.union_raider import kms_union_stat_translator
from simaple.system.union import UnionSquad


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


def parse_block(block: CharacterUnionRaiderBlock) -> tuple[JobType, int]:
    job_type = translate_kms_name(block["block_class"])
    level = block["block_level"]

    if job_type == JobType.virtual_maplestory_m:
        block_size = _get_maplestory_m_block_size(level)
    else:
        block_size = _get_block_size(level)

    return job_type, block_size


def get_union_squad(raider_response: CharacterUnionRaider):

    block_candidates = {block.job: block for block in get_all_blocks()}

    blocks, block_sizes = [], []

    for existing_block in raider_response["union_block"]:
        job_type, block_size = parse_block(existing_block)
        blocks.append(block_candidates[job_type])
        block_sizes.append(block_size)

    return UnionSquad(block_size=block_sizes, blocks=blocks)


def get_union_squad_effect(raider_response: CharacterUnionRaider) -> ExtendedStat:
    translator = kms_union_stat_translator()
    stat = ExtendedStat()

    for expression in raider_response["union_raider_stat"]:
        stat += translator.translate(expression)

    return stat
