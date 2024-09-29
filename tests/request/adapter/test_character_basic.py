from simaple.core import Stat
from simaple.request.adapter.character_basic_loader.adapter import (
    extract_character_ap_based_stat,
)


def test_propensity_response(character_stat_response):
    stat = extract_character_ap_based_stat(character_stat_response)

    assert stat == Stat(
        STR=4,
        DEX=4,
        INT=1438,
        LUK=4,
        MHP=-633,
        MMP=16358,
    )
