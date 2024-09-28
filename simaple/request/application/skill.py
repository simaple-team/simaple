from enum import Enum
from typing import cast

from simaple.request.adapter.nexon_api import (
    HOST,
    CharacterID,
    Token,
    get_character_id_param,
)


class SkillOrder(Enum):
    zero: str = "0"
    first: str = "1"
    first_point_five: str = "1.5"
    second: str = "2"
    second_point_five: str = "2.5"
    third: str = "3"
    fourth: str = "4"
    hyperpassive: str = "hyperpassive"
    hyperactive: str = "hyperactive"
    fifth: str = "5"
    sixth: str = "6"
