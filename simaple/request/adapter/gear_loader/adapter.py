import datetime

from simaple.core import ExtendedStat, Stat
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository
from simaple.gear.symbol_gear import SymbolGear
from simaple.request.adapter.gear_loader._cashitem_converter import get_cash_item_stat
from simaple.request.adapter.gear_loader._converter import get_equipments, get_symbols
from simaple.request.adapter.gear_loader._gearset_converter import get_equipment_stat
from simaple.request.adapter.gear_loader._pet_converter import (
    get_pet_equip_stat_from_response,
)
from simaple.request.adapter.gear_loader._set_item_converter import get_set_item_stats
from simaple.request.external.nexon.api.character.item import (
    get_cash_item_response,
    get_character_item_equipment_response,
    get_character_symbol_response,
    get_pet_equipment_response,
    get_set_effect_response,
)
from simaple.request.external.nexon.api.ocid import (
    as_nexon_datetime,
    get_character_ocid,
)
from simaple.request.service.loader import GearLoader


class NexonAPIGearLoader(GearLoader):
    def __init__(self, host: str, access_token: str, date: datetime.date):
        self._host = host
        self._access_token = access_token
        self._date = date
        self._gear_repository = GearRepository()

    def load_equipments(self, character_name: str) -> list[tuple[Gear, str]]:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        resp = get_character_item_equipment_response(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
        )
        gears = get_equipments(resp, self._gear_repository)
        return gears

    def load_symbols(self, character_name: str) -> list[SymbolGear]:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        resp = get_character_symbol_response(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
        )

        return get_symbols(resp)

    def load_pet_equipments_stat(self, character_name: str) -> Stat:
        ocid = get_character_ocid(self._host, self._access_token, character_name)
        resp = get_pet_equipment_response(
            self._host,
            self._access_token,
            {"ocid": ocid, "date": as_nexon_datetime(self._date)},
        )
        return get_pet_equip_stat_from_response(resp)

    def load_gear_related_stat(self, character_name: str) -> ExtendedStat:
        ocid = get_character_ocid(self._host, self._access_token, character_name)

        equipment_stat = get_equipment_stat(
            get_character_item_equipment_response(
                self._host,
                self._access_token,
                {"ocid": ocid, "date": as_nexon_datetime(self._date)},
            ),
            self._gear_repository,
        )

        pet_equipment_stat = self.load_pet_equipments_stat(character_name)
        symbol_stat = sum(
            (symbol.stat for symbol in self.load_symbols(character_name)), Stat()
        )
        set_item_stat = get_set_item_stats(
            get_set_effect_response(
                self._host,
                self._access_token,
                {"ocid": ocid, "date": as_nexon_datetime(self._date)},
            )
        )
        cash_item_stat = get_cash_item_stat(
            get_cash_item_response(
                self._host,
                self._access_token,
                {"ocid": ocid, "date": as_nexon_datetime(self._date)},
            )
        )

        return equipment_stat + ExtendedStat(
            stat=(pet_equipment_stat + symbol_stat + set_item_stat + cash_item_stat)
        )
