from abc import ABCMeta, abstractmethod
from typing import Optional

from pydantic import BaseModel

from simaple.core import Stat
from simaple.gear.gear import GearMeta


class GearImprovement(BaseModel, metaclass=ABCMeta):
    type: str

    @abstractmethod
    def calculate_improvement(
        self, meta: GearMeta, ref_stat: Optional[Stat] = None
    ) -> Stat:
        ...
