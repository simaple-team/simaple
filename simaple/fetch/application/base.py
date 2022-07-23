from simaple.fetch.element import (
    MapleGearsetElement,
    character_promise,
    item_promise,
    maple_gearset_promise,
    pet_list_promise,
)
from simaple.fetch.token import TokenRepository


class Application:
    ...


class KMSFetchApplication(Application):
    def run(self, name: str):
        token_repository = TokenRepository()
        token = token_repository.get(name)

        item = maple_gearset_promise().then(
            {
                idx: item_promise()
                for idx in set(
                    MapleGearsetElement.expected_normal_names()
                    + MapleGearsetElement.expected_arcane_names()
                )
            }
        )

        character = character_promise()

        pet = pet_list_promise().then({idx: item_promise() for idx in range(3)})

        item_info = item.resolve("", token)
        character_info = character.resolve("", token)
        pet_info = pet.resolve("", token)

        return {"character": character_info, "item": item_info, "pet": pet_info}
