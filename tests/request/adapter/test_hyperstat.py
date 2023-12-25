from simaple.request.adapter.hyperstat import get_hyperstat
from simaple.system.hyperstat import Hyperstat


def test_hyperstat_adapter(character_hyper_stat_response):
    hyperstat = get_hyperstat(character_hyper_stat_response)

    expected = Hyperstat(options=hyperstat.options).get_level_rearranged(
        [0, 0, 6, 1, 0, 13, 12, 12, 13, 5]
    )

    assert hyperstat.get_stat().short_dict() == expected.get_stat().short_dict()
