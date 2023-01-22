import pytest

from simaple.core import Stat
from simaple.gear.gear import Gear, GearMeta
from simaple.gear.gear_repository import GearRepository
from simaple.gear.gear_type import GearType


@pytest.fixture(name="sample_gear")
def fixture_sample_gear():
    return Gear(
        meta=GearMeta(
            id=0,
            name="test-gear",
            req_level=150,
            type=GearType.cap,
            base_stat=Stat(STR=3),
            max_scroll_chance=3,
        ),
        stat=Stat(STR=3),
        scroll_chance=3,
    )


def test_gear_is_immutable(sample_gear: Gear):
    with pytest.raises(Exception):
        sample_gear.meta.name = "new-name"


def test_gear_add_stat(sample_gear: Gear):
    sample_gear = sample_gear.add_stat(Stat(STR=3))
    assert sample_gear.stat == Stat(STR=6)


def test_gear_repository():
    gear_id = 1003797

    repository = GearRepository()
    repository.get_by_id(gear_id)


def test_gear_repository_by_name():
    repository = GearRepository()
    repository.get_by_name("아케인셰이드 메이지글러브")


@pytest.mark.parametrize(
    "gear_id, exists",
    [
        (23456789345678, False),
        (1003797, True),
    ],
)
def test_gear_repository_exist(gear_id, exists):
    repository = GearRepository()
    assert repository.exists(gear_id) == exists


def test_gear_repository_not_exist_raises_error():
    with pytest.raises(KeyError):
        repository = GearRepository()
        repository.get_by_id(234534564567)
