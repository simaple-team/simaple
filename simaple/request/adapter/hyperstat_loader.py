from simaple.core import StatProps
from simaple.data.system.hyperstat import get_kms_hyperstat
from simaple.request.external.nexon.api.character.hyper_stat import (
    CharacterHyperStatResponse,
    HyperStatResponseColumnResponse,
    get_hyper_stat,
)
from simaple.request.external.nexon.client import NexonAPIClient
from simaple.request.service.loader import HyperstatLoader
from simaple.system.hyperstat import Hyperstat


class NexonAPIHyperStatLoader(HyperstatLoader):
    def __init__(self, client: NexonAPIClient):
        self._client = client

    def load_hyper_stat(self, character_name: str) -> Hyperstat:
        hyperstat_response = self._client.session(character_name).request(
            get_hyper_stat
        )
        return get_hyperstat_from_response(hyperstat_response)


_STAT_NAME_TO_BASIS_NAME = {
    "STR": StatProps.STR_static,
    "DEX": StatProps.DEX_static,
    "INT": StatProps.INT_static,
    "LUK": StatProps.LUK_static,
    "공격력/마력": StatProps.attack_power,
    "데미지": StatProps.damage_multiplier,
    "보스 몬스터 공격 시 데미지 증가": StatProps.boss_damage_multiplier,
    "크리티컬 데미지": StatProps.critical_damage,
    "크리티컬 확률": StatProps.critical_rate,
    "방어율 무시": StatProps.ignored_defence,
}


def get_hyperstat_from_response(
    hyperstat_response: CharacterHyperStatResponse,
) -> Hyperstat:
    target_preset: list[HyperStatResponseColumnResponse] = hyperstat_response[
        f"hyper_stat_preset_{int(hyperstat_response['use_preset_no'])}"  # type: ignore
    ]
    hyperstat = get_kms_hyperstat()

    for column in target_preset:
        if column["stat_type"] in _STAT_NAME_TO_BASIS_NAME:
            hyperstat = hyperstat.set_level(
                _STAT_NAME_TO_BASIS_NAME[column["stat_type"]],
                column["stat_level"],
            )

    return hyperstat
