import pytest

from simaple.gear.gear_repository import GearRepository
from simaple.gear.setitem import KMSSetItemRepository

# fmt: off
COUNT_TEST_CASES = [
    ([1004422], 504, 1),
    ([1004422, 1052882,], 504, 2),
    ([1004422, 1052882, 1102775,], 504, 3),
    ([1004422, 1052882, 1073030, 1102775,], 504, 4),
    ([1004422, 1052882, 1073030, 1082636, 1102775,], 504, 5),
    ([1004422, 1052882, 1102775, 1012478], 504, 3),
    ([1004422, 1052882, 1102775, 1053065, 1053402], 504, 3),
]

MEASURE_TEST_CASES = [
    ([1004422,], {504: 1}),
    ([1004422, 1052882,], {504: 2}),
    ([1004422, 1052882, 1102775,], {504: 3}),
    ([1004422, 1052882, 1073030, 1102775,], {504: 4}),
    ([1004422, 1052882, 1073030, 1082636, 1102775,], {504: 5}),
    ([1004422, 1052882, 1073030, 1082636, 1102775, 1053065, 1053402, 1052319], {504: 5, 619: 1, 18: 1}),
    ([1004422, 1052882, 1073030, 1082636, 1102775, 1053065, 1053402], {504: 5, 619: 1}),
    ([1004422, 1082636, 1102775, 1012060, 1053402], {504: 3}),
    ([1004422, 1012060, 1053402], {504: 1}),
    ([1004422, 1052882, 1102775, 1012478, 1022231, 1022232, 1022277, 1032136], {504: 3, 462: 5}),
    ([1004422, 1052882, 1102775, 1012478, 1022231, 1022232,], {504: 3, 462: 3}),
    ([1004422, 1052882, 1102775, 1012478], {504: 3, 462: 1}),
    ([1004422, 1052882, 1102775, 1012478, 1213022], {504: 4, 462: 1}),
    ([1004422, 1052882, 1102775, 1213022], {504: 4}),
    ([1004422, 1052882, 1102775, 1213022, 1032200, 1113055, 1152154], {504: 4, 287: 4}),
]
# fmt: on


@pytest.mark.parametrize("gear_ids, set_item_id, count", COUNT_TEST_CASES)
def test_set_item_count(gear_ids, set_item_id, count):
    gear_repository = GearRepository()
    set_item_repository = KMSSetItemRepository()
    gears = [gear_repository.get_by_id(gear_id) for gear_id in gear_ids]

    set_item = set_item_repository.get(set_item_id)
    assert count == set_item.count(gears)


@pytest.mark.parametrize("gear_ids, expected", MEASURE_TEST_CASES)
def test_set_item_measure(gear_ids, expected):
    gear_repository = GearRepository()
    set_item_repository = KMSSetItemRepository()
    gears = [gear_repository.get_by_id(gear_id) for gear_id in gear_ids]

    set_items = set_item_repository.get_set_item_counts(gears)

    result = {set_item.id: count for set_item, count in set_items}
    assert result == expected
