from abc import ABCMeta, abstractmethod

from simaple.gear.gear import Gear
from simaple.gear.slot_name import SlotName


class AbstractCharacter(metaclass=ABCMeta):
    @abstractmethod
    def get_item(self, slot_name: SlotName) -> Gear:
        ...
