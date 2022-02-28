from simaple.gear.gear_repository import GearRepository
from loguru import logger


def test_gear():
    repository = GearRepository()

    gear_id = 1003797

    repository._get_gear(gear_id)

