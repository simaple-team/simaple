from abc import abstractmethod

from pydantic import BaseModel

from simaple.gear.gear_repository import GearRepository
from simaple.gear.gearset import Gearset
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)


class GearsetBlueprint(BaseModel, metaclass=TaggedNamespacedABCMeta(kind="blueprint")):
    @abstractmethod
    def build(self, gear_repository: GearRepository) -> Gearset:
        ...
