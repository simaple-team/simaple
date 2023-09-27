import json
import os

from simaple.core import Stat
from simaple.gear.gear import Gear, GearMeta
from simaple.gear.gear_type import GearType

GEAR_RESOURCE_PATH = os.path.join(
    os.path.dirname(__file__), "resources", "gear_data.json"
)
GEAR_VARIABLE_NAMES = [
    ("boss_damage_multiplier", "boss_damage_multiplier"),
    ("ignored_defence", "ignored_defence"),
    ("critical_rate", "critical_rate"),
    ("critical_damage", "critical_damage"),
    ("damage_multiplier", "damage_multiplier"),
    ("pdamage_indep", "final_damage_multiplier"),
    ("attack_power", "attack_power"),
    ("magic_attack", "magic_attack"),
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
            "exceptional_enhancement": dumped_gear_meta.get("etuc", False),
        }

        return GearMeta.model_validate(gear_meta_opt)

    def _get_gear(self, gear_id: int) -> Gear:
        return Gear.create_bare_gear(self.get_gear_meta(gear_id))

    def get_by_id(self, gear_id: int) -> Gear:
        gear = self._get_gear(gear_id)
        return gear

    def get_by_name(
        self, gear_name: str, create_empty_item_if_not_exist: bool = False
    ) -> Gear:
        if self._indexed_by_name is None:
            self._indexed_by_name = {}
            for item_id, item_value in self._bare_gears.items():
                if item_value["name"] not in self._indexed_by_name:
                    self._indexed_by_name[item_value["name"]] = int(item_id)

        if self._is_item_name_indicates_arcane_symbol(gear_name):
            return self._get_bare_arcane_symbol(gear_name)

        if gear_name not in self._indexed_by_name and create_empty_item_if_not_exist:
            return self._get_empty_item(gear_name)

        return self.get_by_id(self._indexed_by_name[gear_name])

    def _get_bare_arcane_symbol(self, gear_name: str) -> Gear:
        return Gear(
            meta=GearMeta(
                id=-1,
                name=gear_name,
                base_stat=Stat(),
                type=GearType.arcane_symbol,
                req_level=200,
                max_scroll_chance=0,
            ),
            stat=Stat(),
            scroll_chance=0,
        )

    def _get_empty_item(self, gear_name: str) -> Gear:
        return Gear(
            meta=GearMeta(
                id=-1,
                name=gear_name,
                base_stat=Stat(),
                type=GearType.dummy,
                req_level=0,
                max_scroll_chance=0,
            ),
            stat=Stat(),
            scroll_chance=0,
        )

    def _is_item_name_indicates_arcane_symbol(self, gear_name: str) -> bool:
        return "아케인심볼" in gear_name
