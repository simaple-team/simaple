import pytest

from simaple.core import Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType
from simaple.gear.gearset import Gearset, GearSlot


@pytest.fixture(name="default_gearset")
def get_default_gearset():
    return Gearset()


def test_set_pet_equip_stat(default_gearset):
    default_gearset.set_pet_equip_stat(Stat(INT=5))

    assert default_gearset.pet_equip.INT == 5


def test_set_pet_set_option(default_gearset):
    default_gearset.set_pet_set_option(Stat(INT=5))

    assert default_gearset.pet_set_option.INT == 5


def test_set_cash_item_stat(default_gearset):
    default_gearset.set_cash_item_stat(Stat(INT=5))

    assert default_gearset.cash_item_stat.INT == 5


def test_set_title_stat(default_gearset):
    default_gearset.set_title_stat(Stat(INT=5))

    assert default_gearset.title.INT == 5
