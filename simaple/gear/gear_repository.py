import json
import os

from simaple.gear.gear import Gear, GearMeta
from simaple.gear.gear_type import GearType

GEAR_RESOURCE_PATH = os.path.join(
    os.path.dirname(__file__), "resources", "gear_data.json"
)
GEAR_VARIABLE_NAMES = [
    ("boss_pdamage", "boss_damage_multiplier"),
    ("armor_ignore", "ignored_defence"),
    ("crit", "critical_rate"),
    ("crit_damage", "critical_damage"),
    ("pdamage", "damage_multiplier"),
    ("pdamage_indep", "final_damage_multiplier"),
    ("att", "attack_power"),
    ("matt", "magic_attack"),
    ("MHP", "MHP"),
    ("MMP", "MMP"),
]


class GearRepository:
    def __init__(self):
        self._bare_gears = {}
        self._indexed_by_name = None
        self._load()

    def _load(self):
        with open(GEAR_RESOURCE_PATH, encoding="utf-8") as f:
            self._bare_gears = json.load(f)

    def exists(self, gear_id: int):
        return str(gear_id) in self._bare_gears

    def get_gear_type(self, gear_id: int):
        value = gear_id // 1000
        if value == 1098:
            return GearType.soul_shield
        if value == 1099:
            return GearType.demon_shield
        if value == 1212:
            return GearType.shining_rod
        if value == 1213:
            return GearType.tuner
        if value == 1214:
            return GearType.breath_shooter
        value = gear_id // 10000
        if value == 135:
            value = gear_id // 100
            if value in (13522, 13528, 13529, 13540):
                return GearType(gear_id // 10)
            return GearType(gear_id // 100 * 10)

        if gear_id // 100 == 11902:
            return GearType(gear_id // 10)
        return GearType(gear_id // 10000)

    def get_gear_meta(self, gear_id: int) -> GearMeta:
        dumped_gear_meta = self._bare_gears[str(gear_id)]
        stat = {
            "STR": dumped_gear_meta.get("STR", 0),
            "INT": dumped_gear_meta.get("INT", 0),
            "DEX": dumped_gear_meta.get("DEX", 0),
            "LUK": dumped_gear_meta.get("LUK", 0),
        }

        for k, v in dumped_gear_meta.items():
            for variable_name, simaple_name in GEAR_VARIABLE_NAMES:
                if variable_name == k:
                    stat[simaple_name] = v
                    break

        gear_meta_opt = {
            "id": gear_id,
            "name": dumped_gear_meta["name"],
            "req_level": dumped_gear_meta.get("req_level", 0),
            "boss_reward": dumped_gear_meta.get("boss_reward", False),
            "superior_eqp": dumped_gear_meta.get("superior_eqp", False),
            "req_job": dumped_gear_meta.get("req_job", 0),
            "set_item_id": dumped_gear_meta.get("set_item_id", 0),
            "joker_to_set_item": dumped_gear_meta.get("joker_to_set_item", False),
            "type": self.get_gear_type(gear_id),
            "base_stat": stat.copy(),
            "max_scroll_chance": dumped_gear_meta.get("tuc", 0),
        }

        return GearMeta.parse_obj(gear_meta_opt)

    def _get_gear(self, gear_id: int) -> Gear:
        return Gear.create_bare_gear(self.get_gear_meta(gear_id))

    def get_by_id(self, gear_id: int) -> Gear:
        gear = self._get_gear(gear_id)
        return gear

    def get_by_name(self, gear_name: str) -> Gear:
        if self._indexed_by_name is None:
            self._indexed_by_name = {}
            for item_id, item_value in self._bare_gears.items():
                self._indexed_by_name[item_value["name"]] = int(item_id)

        return self.get_by_id(self._indexed_by_name[gear_name])
