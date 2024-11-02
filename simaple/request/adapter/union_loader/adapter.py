import datetime

from simaple.core import ExtendedStat, JobType
from simaple.data.system.artifact import get_artifact_effects
from simaple.data.system.union_block import get_all_blocks
from simaple.request.adapter.translator.job_name import translate_kms_name
from simaple.request.adapter.translator.kms.union_raider import (
    kms_union_stat_translator,
)
from simaple.request.adapter.union_loader._converter import (
    get_stat_from_occupation_description,
)
from simaple.request.external.nexon.api.character.union import (
    CharacterUnionRaiderBlock,
    CharacterUnionRaiderPreset,
    UnionArtifactResponse,
    get_character_union_raider_response,
    get_union_artifact_response,
)
from simaple.request.external.nexon.api.ocid import (
    as_nexon_datetime,
    get_character_ocid,
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
        return get_union_squad(resp)

    def load_union_squad_effect(self, character_name: str) -> ExtendedStat:
        resp = self._client.session(character_name).request(
            get_character_union_raider_response
        )
        return get_union_squad_effect(resp)

    def load_union_artifact(self, character_name: str) -> Artifact:
        resp = self._client.session(character_name).request(get_union_artifact_response)
        return get_union_artifact(resp)

    def load_union_occupation_stat(self, character_name: str) -> ExtendedStat:
        resp = self._client.session(character_name).request(
            get_character_union_raider_response
        )
        return get_occupation_stat(resp)

    def load_best_union_stat(
        self, character_name: str, selector: BestStatSelector
    ) -> ExtendedStat:
        resp = self._client.session(character_name).request(
            get_character_union_raider_response
        )
        candidates = [
            get_occupation_stat(preset) + get_union_squad_effect(preset)
            for preset in [
                resp["union_raider_preset_1"],
                resp["union_raider_preset_2"],
                resp["union_raider_preset_3"],
            ]
        ]

        best_candidate_index = get_best_stat_index(candidates, selector)
        return candidates[best_candidate_index]


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
    level = int(block["block_level"])

    if job_type == JobType.virtual_maplestory_m:
        block_size = _get_maplestory_m_block_size(level)
    else:
        block_size = _get_block_size(level)

    return job_type, block_size


def get_union_squad(raider_response: CharacterUnionRaiderPreset) -> UnionSquad:

    block_candidates = {block.job: block for block in get_all_blocks()}

    blocks, block_sizes = [], []

    for existing_block in raider_response["union_block"]:
        job_type, block_size = parse_block(existing_block)
        blocks.append(block_candidates[job_type])
        block_sizes.append(block_size)

    return UnionSquad(block_size=block_sizes, blocks=blocks)


def get_union_squad_effect(
    raider_response: CharacterUnionRaiderPreset,
) -> ExtendedStat:
    translator = kms_union_stat_translator()
    stat = ExtendedStat()

    for expression in raider_response["union_raider_stat"]:
        stat += translator.translate(expression)

    return stat


def get_occupation_stat(response: CharacterUnionRaiderPreset) -> ExtendedStat:
    return sum(
        [
            get_stat_from_occupation_description(expression)
            for expression in response["union_occupied_stat"]
        ],
        ExtendedStat(),
    )


def get_union_artifact(
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
