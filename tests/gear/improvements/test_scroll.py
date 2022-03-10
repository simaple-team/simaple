from simaple.core.base import Stat
from simaple.gear.gear_type import GearType
from simaple.gear.improvements.scroll import Scroll


def test_acceptable_scroll_if_not_given(test_gear_repository):
    scroll = Scroll(name="test_scroll", stat=Stat(STR=3))

    gear = test_gear_repository.get_by_name("하이네스 던위치햇")
    assert scroll.is_gear_acceptable(gear)


def test_acceptable_scroll(test_gear_repository):
    scroll = Scroll(name="test_scroll", stat=Stat(STR=3), gear_types=[GearType.cap])

    gear = test_gear_repository.get_by_name("하이네스 던위치햇")
    assert scroll.is_gear_acceptable(gear)


def test_unacceptable_scroll(test_gear_repository):
    scroll = Scroll(name="test_scroll", stat=Stat(STR=3), gear_types=[GearType.glove])

    gear = test_gear_repository.get_by_name("하이네스 던위치햇")
    assert not scroll.is_gear_acceptable(gear)
