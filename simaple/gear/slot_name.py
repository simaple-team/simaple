from __future__ import annotations

import enum
from typing import Optional


class SlotName(enum.Enum):
    ### General Equipments ###
    ring1 = "ring1"
    ring2 = "ring2"
    ring3 = "ring3"
    ring4 = "ring4"
    pocket = "pocket"

    pendant2 = "pendant2"
    pendant1 = "pendant1"

    weapon = "weapon"
    belt = "belt"

    cap = "cap"
    face_accessory = "face_accessory"
    eye_accessory = "eye_accessory"
    coat = "coat"
    pants = "pants"
    shoes = "shoes"

    earrings = "earrings"
    shoulder_pad = "shoulder_pad"
    glove = "glove"
    android = "android"

    emblem = "emblem"
    badge = "badge"
    medal = "medal"
    subweapon = "subweapon"
    cape = "cape"
    machine_heart = "machine_heart"

    ### Cash Equipments ###
    cash_ring1 = "cash_ring1"
    cash_ring2 = "cash_ring2"
    cash_ring3 = "cash_ring3"
    cash_ring4 = "cash_ring4"

    cash_weapon = "cash_weapon"
    cash_belt = "cash_belt"

    cash_cap = "cash_cap"
    cash_face_accessory = "cash_face_accessory"
    cash_eye_accessory = "cash_eye_accessory"
    cash_coat = "cash_coat"
    cash_pants = "cash_pants"
    cash_shoes = "cash_shoes"

    cash_earrings = "cash_earrings"
    cash_glove = "cash_glove"

    cash_hair = "cash_hair"
    cash_emotion = "cash_emotion"
    cash_subweapon = "cash_subweapon"
    cash_cape = "cash_cape"

    arcane1 = "arcane1"
    arcane2 = "arcane2"
    arcane3 = "arcane3"
    arcane4 = "arcane4"
    arcane5 = "arcane5"
    arcane6 = "arcane6"

    authentic1 = "authentic1"
    authentic2 = "authentic2"
    authentic3 = "authentic3"
    authentic4 = "authentic4"
    authentic5 = "authentic5"
    authentic6 = "authentic6"

    @classmethod
    def normal_item_grid(cls) -> list[list[Optional[SlotName]]]:
        # fmt: off
        return [
            [SlotName.ring1, None, SlotName.cap, None, SlotName.emblem],
            [SlotName.ring2, SlotName.pendant2, SlotName.face_accessory, None, SlotName.badge],
            [SlotName.ring3, SlotName.pendant1, SlotName.eye_accessory, SlotName.earrings, SlotName.medal],
            [SlotName.ring4, SlotName.weapon, SlotName.coat, SlotName.shoulder_pad, SlotName.subweapon],
            [SlotName.pocket, SlotName.belt, SlotName.pants, SlotName.glove, SlotName.cape],
            [None, None, SlotName.shoes, SlotName.android, SlotName.machine_heart],
        ]
        # fmt: on

    @classmethod
    def cash_item_grid(cls) -> list[list[Optional[SlotName]]]:
        # fmt: off
        return [
            [SlotName.cash_ring1, None, SlotName.cash_cap, None, SlotName.cash_hair],
            [SlotName.cash_ring2, None, SlotName.cash_face_accessory, None, SlotName.cash_emotion],
            [SlotName.cash_ring3, None, SlotName.cash_eye_accessory, SlotName.cash_earrings, None],
            [SlotName.cash_ring4, SlotName.cash_weapon, SlotName.cash_coat, None, SlotName.cash_subweapon],
            [None, None, SlotName.cash_pants, SlotName.cash_glove, SlotName.cash_cape],
            [None, None, SlotName.cash_shoes, None, None],
        ]
        # fmt: on

    @classmethod
    def arcane_items(cls) -> list[SlotName]:
        return [
            SlotName.arcane1,
            SlotName.arcane2,
            SlotName.arcane3,
            SlotName.arcane4,
            SlotName.arcane5,
            SlotName.arcane6,
        ]
