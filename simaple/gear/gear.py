from __future__ import annotations

from pydantic import BaseModel, Extra, Field

from simaple.core import ExtendedStat, Stat
from simaple.gear.gear_type import GearType
from simaple.gear.potential import AdditionalPotential, Potential


class GearMeta(BaseModel):
    id: int
    name: str
    base_stat: Stat
    type: GearType
    req_level: int
    boss_reward: bool = False
    superior_eqp: bool = False
    req_job: int = 0
    set_item_id: int = 0
    joker_to_set_item: bool = False
    max_scroll_chance: int

    class Config:
        extra = Extra.forbid
        validate_assignment = True
        allow_mutation = False

    def show(self) -> str:
        job_string = (
            "["
            + ("] [").join(
                [(" V " if self.req_job & (1 << i) != 0 else "   ") for i in range(5)]
            )
            + "]"
        )

        return f"""
        ===================================
        name: {self.name}
        type: {self.type.name} (type number {self.type})
        req_level: {self.req_level}
                 [WAR] [MAG] [ARC] [THF] [PIR]
        req_job: {job_string}
        """


class Gear(BaseModel):
    meta: GearMeta
    stat: Stat
    scroll_chance: int
    potential: Potential = Field(default_factory=Potential)
    additional_potential: AdditionalPotential = Field(
        default_factory=AdditionalPotential
    )

    class Config:
        extra = Extra.forbid
        validate_assignment = True
        allow_mutation = False

    @classmethod
    def create_bare_gear(cls, meta: GearMeta) -> Gear:
        return Gear(
            meta=meta,
            stat=meta.base_stat.copy(),
            scroll_chance=meta.max_scroll_chance,
        )

    def add_stat(self, stat: Stat) -> Gear:
        serailized_gear = self.dict()
        serailized_gear["stat"] = Stat.parse_obj(serailized_gear["stat"]) + stat

        return Gear.parse_obj(serailized_gear)

    def set_potential(self, potential: Potential) -> Gear:
        serailized_gear = self.dict()
        serailized_gear["potential"] = potential.dict()

        return Gear.parse_obj(serailized_gear)

    def set_additional_potential(
        self, additional_potential: AdditionalPotential
    ) -> Gear:
        serailized_gear = self.dict()
        serailized_gear["additional_potential"] = additional_potential.dict()

        return Gear.parse_obj(serailized_gear)

    def sum_stat(self) -> Stat:
        return self.sum_extended_stat().stat

    def sum_extended_stat(self) -> ExtendedStat:
        potential_extended_stats = (
            self.potential.get_extended_stat()
            + self.additional_potential.get_extended_stat()
        )
        return ExtendedStat(stat=self.stat) + potential_extended_stats

    def show(self) -> str:
        return f"""
        {self.meta.show()}
        ===================================
        Basis Stats

        STR: {self.stat.STR}
        DEX: {self.stat.DEX}
        INT: {self.stat.INT}
        LUK: {self.stat.LUK}
        
        MaxHP: {self.stat.MHP}
        MaxMP: {self.stat.MMP}

        ATT: {self.stat.attack_power}
        MAT: {self.stat.magic_attack}

        ===================================
        """
