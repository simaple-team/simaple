import asyncio

from simaple.fetch.element import (
    MapleGearsetElement,
    character_promise,
    maple_gearset_promise,
    pet_list_promise,
    standard_gear_promise,
)
from simaple.fetch.response.character import CharacterResponse
from simaple.fetch.token import TokenRepository
from simaple.fetch.translator.gear import GearTranslator
from simaple.fetch.translator.kms.gear import kms_gear_stat_translator
from simaple.fetch.translator.kms.potential import kms_potential_translator
from simaple.gear.gear_repository import GearRepository


class Application:
    ...


class KMSFetchApplication(Application):
    def __init__(self):
        self._translator = GearTranslator(
            gear_stat_translator=kms_gear_stat_translator(),
            potential_translator=kms_potential_translator(),
            gear_repository=GearRepository(),
        )

    def run(self, name: str):
        raw = asyncio.run(self.async_run(name))

        return CharacterResponse(raw, self._translator)

    async def async_run(self, name: str):
        token_repository = TokenRepository()
        token = token_repository.get(name)

        item = maple_gearset_promise().then(
            {
                idx: standard_gear_promise()
                for idx in set(
                    MapleGearsetElement.expected_normal_names()
                    + MapleGearsetElement.expected_arcane_names()
                    + MapleGearsetElement.expected_cash_names()
                )
            }
        )

        character = character_promise()

        pet = pet_list_promise().then(
            {str(idx): standard_gear_promise() for idx in range(3)}
        )

        futures = [
            asyncio.ensure_future(item.resolve("", token)),
            asyncio.ensure_future(character.resolve("", token)),
            asyncio.ensure_future(pet.resolve("", token)),
        ]
        item_info, character_info, pet_info = await asyncio.gather(*futures)

        return {"character": character_info, "item": item_info, "pet": pet_info}
