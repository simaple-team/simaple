from typing import cast
from simaple.core import Stat, ExtendedStat
from simaple.request.adapter.nexon_api import (
    HOST,
    Token,
    get_character_id,
    get_character_id_param,
)
from simaple.request.service.loader import GearLoader
from simaple.gear.gear import Gear
from simaple.request.adapter.gear_loader._schema import (
    CharacterItemEquipment,
    CharacterSymbolEquipment,
    PetResponse,
)
from simaple.request.adapter.gear_loader._converter import (
    get_equipments, get_symbols
)
from simaple.request.adapter.gear_loader._gearset_converter import (
    get_gearset
)
from simaple.request.adapter.gear_loader._pet_converter import (
    get_pet_equip_stat_from_response
)
from simaple.gear.gear_repository import GearRepository
from simaple.gear.symbol_gear import SymbolGear


class NexonAPIGearLoader(GearLoader):
    def __init__(self, token_value: str):
        self._token = Token(token_value)
        self._gear_repository = GearRepository()

    async def load_equipments(self, character_name: str) -> list[tuple[Gear, str]]:
        character_id = await get_character_id(self._token, character_name)
        uri = f"{HOST}/maplestory/v1/character/item-equipment"

        resp = cast(
            CharacterItemEquipment,
            await self._token.request(uri, get_character_id_param(character_id))
        )
        gears = get_equipments(resp, self._gear_repository)
        return gears

    async def load_symbols(self, character_name: str) -> list[SymbolGear]:
        character_id = await get_character_id(self._token, character_name)
        uri = f"{HOST}/maplestory/v1/character/symbol-equipment"

        resp = cast(
            CharacterSymbolEquipment,
            await self._token.request(uri, get_character_id_param(character_id))
        )
        return get_symbols(resp)

    async def load_pet_equipments_stat(self, character_name: str) -> Stat:
        character_id = await get_character_id(self._token, character_name)
        uri = f"{HOST}/maplestory/v1/character/pet"
        resp = cast(
            PetResponse, await self._token.request(uri, get_character_id_param(character_id))
        )
        return get_pet_equip_stat_from_response(resp)
