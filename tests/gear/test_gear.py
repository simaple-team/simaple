from simaple.gear.gear_repository import GearRepository


def test_gear():
    gear_id = 1003797

    repository = GearRepository()
    repository.get_by_id(gear_id)
