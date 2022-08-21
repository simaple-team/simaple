import math
from typing import Literal, Tuple

from simaple.core import Stat, StatProps
from simaple.gear.gear import Gear
from simaple.gear.gear_type import GearType
from simaple.gear.improvements.base import GearImprovement

PROBABILITIES = [100, 70, 30, 15]
STAT_PROP_TYPES = [
    StatProps.INT,
    StatProps.DEX,
    StatProps.LUK,
    StatProps.STR,
    StatProps.MHP,
]

_WEAPON_IMPROVEMENTS_ATT_STAT = {
    100: [[1, 0], [2, 0], [3, 1]],
    70: [[2, 0], [3, 1], [5, 2]],
    30: [[3, 1], [5, 2], [7, 3]],
    15: [[5, 2], [7, 3], [9, 4]],
}

_GLOBE_IMPROVEMENTS_ATT = {
    100: [0, 1, 1],
    70: [1, 2, 2],
    30: [2, 3, 3],
}

_ARMOR_IMPROVEMENTS_STAT_MHP_PDD = {
    100: [[1, 5, 1], [2, 20, 2], [3, 30, 3]],
    70: [[2, 15, 2], [3, 40, 4], [4, 70, 5]],
    30: [[3, 30, 4], [5, 70, 7], [7, 120, 10]],
}

_ACCESORY_IMPROVEMENTS_STAT = {
    100: [1, 1, 2],
    70: [2, 2, 3],
    30: [3, 4, 5],
}

_MACHINE_HEART_IMPROVEMENTS_STAT = {
    100: [1, 2, 3],
    70: [2, 3, 5],
    30: [3, 5, 7],
}


class SpellTrace(GearImprovement):
    type: Literal["SpellTrace"] = "SpellTrace"
    probability: int
    stat_prop_type: StatProps
    order: int = -1

    def get_spell_trace_rank(self, gear: Gear) -> int:
        return 2 if gear.req_level > 110 else (1 if gear.req_level > 70 else 0)

    def get_weapon_improvement(self, gear: Gear) -> Tuple[int, int, int]:
        attack_basis, stat_basis = _WEAPON_IMPROVEMENTS_ATT_STAT[self.probability][
            self.get_spell_trace_rank(gear)
        ]
        if self.stat_prop_type is StatProps.MHP:
            stat_basis = stat_basis * 50

        return attack_basis, stat_basis, 0

    def get_glove_improvement(self, gear: Gear) -> Tuple[int, int, int]:
        attack_basis = _GLOBE_IMPROVEMENTS_ATT[self.probability][
            self.get_spell_trace_rank(gear)
        ]
        stat_basis = 1 if attack_basis == 0 else 0

        return attack_basis, stat_basis, 0

    def get_armor_improvement(self, gear: Gear) -> Tuple[int, int, int]:
        stat_basis, additional_mhp, _ = _ARMOR_IMPROVEMENTS_STAT_MHP_PDD[
            self.probability
        ][
            self.get_spell_trace_rank(gear)
        ]  # third value is PDD
        if self.stat_prop_type is StatProps.MHP:
            stat_basis, additional_mhp = 0, additional_mhp + stat_basis * 50

        return 0, stat_basis, additional_mhp

    def get_accesory_improvement(self, gear: Gear) -> Tuple[int, int, int]:
        stat_basis = _ACCESORY_IMPROVEMENTS_STAT[self.probability][
            self.get_spell_trace_rank(gear)
        ]
        if self.stat_prop_type is StatProps.MHP:
            stat_basis = stat_basis * 50

        return 0, stat_basis, 0

    def get_machine_heart_improvement(self, gear: Gear) -> Tuple[int, int, int]:
        attack_basis = _MACHINE_HEART_IMPROVEMENTS_STAT[self.probability][
            self.get_spell_trace_rank(gear)
        ]
        return attack_basis, 0, 0

    def calculate_improvement(self, gear: Gear) -> Stat:
        improvement = Stat()
        if self.probability not in PROBABILITIES:
            raise TypeError("Invalid probability: " + str(self.probability))

        if self.stat_prop_type not in STAT_PROP_TYPES:
            raise TypeError(f"Invalid prop_type: {self.stat_prop_type.value}")

        req_job: int = gear.req_job

        attack_type = (
            StatProps.magic_attack
            if self.stat_prop_type == StatProps.INT
            else StatProps.attack_power
        )

        if gear.is_weapon() or gear.type == GearType.katara:
            attack_basis, stat_basis, additional_mhp = self.get_weapon_improvement(gear)
        elif gear.type == GearType.glove:
            attack_basis, stat_basis, additional_mhp = self.get_glove_improvement(gear)
        elif gear.is_armor() or gear.type == GearType.shoulder_pad:
            attack_basis, stat_basis, additional_mhp = self.get_armor_improvement(gear)
        elif gear.is_accessory():
            attack_basis, stat_basis, additional_mhp = self.get_accesory_improvement(
                gear
            )
        elif gear.type == GearType.machine_heart:
            (
                attack_basis,
                stat_basis,
                additional_mhp,
            ) = self.get_machine_heart_improvement(gear)

        improvement += Stat.parse_obj(
            {attack_type.value: attack_basis, self.stat_prop_type.value: stat_basis}
        )

        improvement += Stat(MHP=additional_mhp)

        if (gear.is_armor()) and self.order == 4 and gear.type != GearType.glove:
            improvement += Stat(
                magic_attack=int(
                    gear.req_job == 0 or math.floor(gear.req_job / 2) % 2 == 1
                ),
                attack_power=int(
                    gear.req_job == 0 or math.floor(gear.req_job / 2) % 2 == 0
                ),
            )

        return improvement
