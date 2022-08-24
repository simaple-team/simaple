import copy

from simaple.character.character import AbstractCharacter
from simaple.fetch.translator.gear import GearTranslator
from simaple.gear.gear import Gear
from simaple.gear.slot_name import SlotName


class CharacterResponse(AbstractCharacter):
    def __init__(self, raw: dict, gear_translator: GearTranslator):
        self._raw = raw
        self._gear_translator = gear_translator

    def get_character_base_stat(self):
        ...

    def get_item(self, slot_name: SlotName) -> Gear:
        dumped = self._raw["item"].get(slot_name.value)
        return self._gear_translator.translate(dumped)

    def get_raw(self):
        return copy.deepcopy(self._raw)
