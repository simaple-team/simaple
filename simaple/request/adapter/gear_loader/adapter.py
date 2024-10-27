import datetime
from typing import cast

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
from simaple.request.external.nexon.api.auth import (
    HOST,
    CharacterID,
    Token,
    get_character_id,
    get_character_id_param,
)
from simaple.request.external.nexon.schema.character.item import (
    CashItemResponse,
    CharacterItemEquipment,
    CharacterSymbolEquipment,
    PetResponse,
    SetEffectResponse,
)
from simaple.request.service.loader import GearLoader


class NexonAPIGearLoader(GearLoader):
    def __init__(self, token_value: str, date: datetime.date | None = None):
        self._token = Token(token_value)
        self._gear_repository = GearRepository()
        self.date = date

    def get_character_id(self, character_name: str) -> CharacterID:
        return get_character_id(self._token, character_name, date=self.date)

    def load_equipments(self, character_name: str) -> list[tuple[Gear, str]]:
        character_id = self.get_character_id(character_name)
        uri = f"{HOST}/maplestory/v1/character/item-equipment"

        resp = cast(
            CharacterItemEquipment,
            self._token.request(uri, get_character_id_param(character_id)),
        )
        gears = get_equipments(resp, self._gear_repository)
        return gears

    def load_symbols(self, character_name: str) -> list[SymbolGear]:
        character_id = self.get_character_id(character_name)
        uri = f"{HOST}/maplestory/v1/character/symbol-equipment"

        resp = cast(
            CharacterSymbolEquipment,
            self._token.request(uri, get_character_id_param(character_id)),
        )
        return get_symbols(resp)

    def load_pet_equipments_stat(self, character_name: str) -> Stat:
        character_id = self.get_character_id(character_name)
        uri = f"{HOST}/maplestory/v1/character/pet-equipment"
        resp = cast(
            PetResponse,
            self._token.request(uri, get_character_id_param(character_id)),
        )
        return get_pet_equip_stat_from_response(resp)

    def load_gear_related_stat(self, character_name: str) -> ExtendedStat:
        character_id = self.get_character_id(character_name)

        equipment_stat = get_equipment_stat(
            cast(
                CharacterItemEquipment,
                self._token.request(
                    f"{HOST}/maplestory/v1/character/item-equipment",
                    get_character_id_param(character_id),
                ),
            ),
            self._gear_repository,
        )

        pet_equipment_stat = self.load_pet_equipments_stat(character_name)
        symbol_stat = sum(
            (symbol.stat for symbol in self.load_symbols(character_name)), Stat()
        )
        set_item_stat = get_set_item_stats(
            cast(
                SetEffectResponse,
                self._token.request(
                    f"{HOST}/maplestory/v1/character/set-effect",
                    get_character_id_param(character_id),
                ),
            )
        )
        cash_item_stat = get_cash_item_stat(
            cast(
                CashItemResponse,
                self._token.request(
                    f"{HOST}/maplestory/v1/character/cashitem-equipment",
                    get_character_id_param(character_id),
                ),
            )
        )

        return equipment_stat + ExtendedStat(
            stat=(pet_equipment_stat + symbol_stat + set_item_stat + cash_item_stat)
        )
