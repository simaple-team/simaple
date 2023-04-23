import pytest

from simaple.gear.gear_repository import GearRepository


@pytest.fixture(name="test_gear_repository")
def fixture_test_gear_repository() -> GearRepository:
    return GearRepository()
