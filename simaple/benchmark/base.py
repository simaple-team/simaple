from abc import ABCMeta, abstractmethod

from pydantic import BaseModel

from simaple.gear.gear_repository import GearRepository
from simaple.gear.gearset import Gearset


class GearsetBlueprint(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def build(self, gear_repository: GearRepository) -> Gearset:
        ...
