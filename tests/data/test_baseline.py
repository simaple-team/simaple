import pytest

from simaple.core import BaseStatType, JobCategory, JobType
from simaple.data.baseline import get_baseline_gearset
from simaple.gear.gearset import Gearset


@pytest.mark.parametrize(
    "baseline_name",
    [
        "Epic",
        "EpicUnique",
        "Unique",
        "Legendary18",
        "LegendaryHalf",
        "Legendary",
    ],
)
def test_interpreter_get_gearset(baseline_name: str) -> None:
    gearset: Gearset = get_baseline_gearset(
        baseline_name,
        JobCategory.warrior,
        JobType.adele,
    )
    assert gearset.get_total_extended_stat()


def test_gearset_ok() -> None:
    gearset: Gearset = get_baseline_gearset(
        "Legendary",
        JobCategory.warrior,
        JobType.adele,
    )

    assert (
        int(
            gearset.get_total_extended_stat().stat.get_base_stat_coefficient(
                BaseStatType.STR
            )
        )
        == 44964
    )
