import pytest

from simaple.gear.gear_repository import GearRepository


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
