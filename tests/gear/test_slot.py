import pytest

from simaple.core import Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType
from simaple.gear.gearset import Gearset, GearSlot


class MetaTestcase:
    def get_slot(self, slot_name, enabled_gear_types):
        return GearSlot(
            name=slot_name,
            enabled_gear_types=enabled_gear_types,
        )

    def get_test_gear(self, gear_type):
        return Gear(
            type=gear_type,
            id=0,
            stat=Stat(),
            name="test_gear",
            req_level=0,
            scroll_chance=0,
            boss_reward=False,
            superior_eqp=False,
        )


@pytest.mark.parametrize(
    "slot_name, enabled_gear_types, test_gear_type",
    [
        ("single-type", [GearType.cape], GearType.cape),
        ("multi-type", [GearType.cape, GearType.shoes], GearType.cape),
    ],
)
class TestGoodCases(MetaTestcase):
    def test_gear_slot_is_equippable_method(
        self, slot_name, enabled_gear_types, test_gear_type
    ):
        slot = self.get_slot(slot_name, enabled_gear_types)
        gear = self.get_test_gear(test_gear_type)

        assert slot.is_equippable(gear)

    def test_gear_slot_equips(self, slot_name, enabled_gear_types, test_gear_type):
        slot = self.get_slot(slot_name, enabled_gear_types)
        gear = self.get_test_gear(test_gear_type)

        slot.equip(gear)
        assert slot.is_equipped()


@pytest.mark.parametrize(
    "slot_name, enabled_gear_types, test_gear_type",
    [
        ("single-type-reject", [GearType.shoes], GearType.glove),
        ("multi-type-reject", [GearType.cape, GearType.shoes], GearType.glove),
    ],
)
class TestBadCases(MetaTestcase):
    def test_gear_slot_is_equippable_method(
        self, slot_name, enabled_gear_types, test_gear_type
    ):
        slot = self.get_slot(slot_name, enabled_gear_types)
        gear = self.get_test_gear(test_gear_type)

        assert not slot.is_equippable(gear)

    def test_gear_slot_fails_equip(self, slot_name, enabled_gear_types, test_gear_type):
        slot = self.get_slot(slot_name, enabled_gear_types)
        gear = self.get_test_gear(test_gear_type)

        with pytest.raises(ValueError):
            slot.equip(gear)
