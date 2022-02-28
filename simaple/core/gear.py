from pydantic import BaseModel
from simaple.core.base import Stat
from typing import List
import enum
import json

class GearType(enum.Enum):
    armor = 'armor'
    accesory = 'accesory'


class Gear(BaseModel):
    stat: Stat
    name: str
    type: GearType
    req_level: int



class Scroll(BaseModel):
    stat: Stat
    name: str
    gear_types: List[GearType]


class GearImprovement(BaseModel):
    starforce: int
    scrolls: List[Scroll]



class GearRepository:
    def __init__(self):
        self._bare_gears = {} 

    def _load(self):
        GEAR_RESOURCE_PATH = "simaple/resource/gear_data.json"
        with open(GEAR_RESOURCE_PATH) as f:
            self._bare_gears = json.load(f)


    def _get_gear(self, gear_name: str) -> Stat:

        gear = Gear()
        gear.name = node['name']
        gear.item_id = gear_id
        gear.type = Gear.get_gear_type(gear_id)
        for key in node:
            value: int = node[key]
            if key in ("STR", "DEX", "INT", "LUK", "att", "matt", "MHP", "MMP", "MHP_rate", "MMP_rate",
                       "boss_pdamage", "armor_ignore", "crit", "crit_damage", "pdamage", "pdamage_indep"):
                prop_type = GearPropType[key]
                gear.base_stat[prop_type] = value
            else:
                if isinstance(getattr(gear, key), bool):
                    value = bool(value)
                setattr(gear, key, value)
        gear.max_star = gear.get_max_star()
        return gear

    def get_gear(self, gear_name: str, improvement: GearImprovement):
        ...
