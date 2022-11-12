from typing import Optional

import pydantic

from simaple.core.base import Stat
from simaple.simulate.view import AggregationView


class Validity(pydantic.BaseModel):
    name: str
    time_left: float
    valid: bool


class ValidityParentView(AggregationView):
    """A View for valid-skill set
    Gathers view name `validity`, returns each component's validity(which
     meant whether given component can dispatch `use` action by Player)
    """

    def aggregate(self, representations: list[Validity]):
        return representations

    @classmethod
    def get_installation_pattern(cls):
        return r".*\.validity"


class BuffParentView(AggregationView):
    def aggregate(self, representations: list[Optional[Stat]]):
        total_buff = Stat()
        for buff_stat in representations:
            if buff_stat is not None:
                total_buff += buff_stat

        return total_buff

    @classmethod
    def get_installation_pattern(cls):
        return r".*\.buff"
