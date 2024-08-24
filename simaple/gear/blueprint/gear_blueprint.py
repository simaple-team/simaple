from abc import ABCMeta, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from simaple.core import Stat
from simaple.gear.blueprint.potential_blueprint import (
    PotentialTemplate,
    PotentialTierTable,
    PotentialType,
    template_to_potential,
)
from simaple.gear.bonus_factory import BonusFactory, BonusType
from simaple.gear.gear import Gear, GearMeta
from simaple.gear.improvements.exceptional_enhancement import ExceptionalEnhancement
from simaple.gear.improvements.scroll import Scroll
from simaple.gear.improvements.spell_trace import SpellTrace
from simaple.gear.improvements.starforce import Starforce


class AbstractGearBlueprint(BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def build(self) -> Gear: ...


class BonusSpec(BaseModel):
    bonus_type: BonusType
    grade: Optional[int] = None
    rank: Optional[int] = None

    @field_validator("grade")
    @classmethod
    def rank_may_in_proper_range(cls, v):
        if v is not None:
            if not 1 <= v <= 7:
                raise ValueError("grade may in range 1~7")

        return v

    @model_validator(mode="after")
    def rank_and_grade_may_not_given_together(self):
        if self.grade and self.rank:
            raise ValueError("grade and rank may not given together.")
        if self.grade is None and self.rank is None:
            raise ValueError("grade or rank may given.")

        if self.rank:
            if not 1 <= self.rank <= 7:
                raise ValueError("rank may in range 1~7")

        return self

    def get_grade(self) -> int:
        if self.grade:
            return self.grade

        if self.rank is None:
            raise ValueError("rank and grade may not both None.")

        return 8 - self.rank


def _get_bonus_from_spec(bonus_factory: BonusFactory, bonus_spec: BonusSpec):
    return bonus_factory.create(bonus_spec.bonus_type, bonus_spec.get_grade())


class GeneralizedGearBlueprint(AbstractGearBlueprint):
    meta: GearMeta
    spell_traces: List[SpellTrace] = []
    scrolls: List[Scroll] = []
    starforce: Starforce
    bonuses: List[BonusSpec] = []
    potential: PotentialTemplate = Field(default_factory=PotentialTemplate)
    additional_potential: PotentialTemplate = Field(default_factory=PotentialTemplate)
    exceptional_enhancement: Optional[ExceptionalEnhancement] = None

    def build(self) -> Gear:
        gear_stat = self.meta.base_stat.model_copy()

        # Apply spell trace and scroll, starforce
        spell_trace_and_scoll_stat = sum(
            [
                spell_trace.calculate_improvement(self.meta)
                for spell_trace in self.spell_traces
            ],
            Stat(),
        ) + sum(
            [scroll.calculate_improvement(self.meta) for scroll in self.scrolls],
            Stat(),
        )
        gear_stat += spell_trace_and_scoll_stat
        gear_stat += self.starforce.calculate_improvement(self.meta, ref_stat=gear_stat)

        # Apply bonus
        bonus_factory = BonusFactory()
        bonuses = [_get_bonus_from_spec(bonus_factory, spec) for spec in self.bonuses]

        bonus_stat = sum(
            [bonus.calculate_improvement(self.meta) for bonus in bonuses],
            Stat(),
        )

        potential_table = PotentialTierTable.kms()

        gear_stat += bonus_stat

        if self.exceptional_enhancement:
            gear_stat += self.exceptional_enhancement.calculate_improvement(self.meta)

        return Gear(
            meta=self.meta,
            stat=gear_stat,
            scroll_chance=self.meta.max_scroll_chance,
            potential=template_to_potential(
                self.potential,
                potential_table,
                self.meta.req_level,
                PotentialType.get_type(
                    is_additional=False, is_weapon=self.meta.type.is_weaponry()
                ),
            ),
            additional_potential=template_to_potential(
                self.additional_potential,
                potential_table,
                self.meta.req_level,
                PotentialType.get_type(
                    is_additional=True, is_weapon=self.meta.type.is_weaponry()
                ),
            ),
        )


class PracticalGearBlueprint(AbstractGearBlueprint):
    meta: GearMeta
    spell_trace: Optional[SpellTrace] = None
    scroll: Optional[Scroll] = None
    star: int = 0
    bonuses: List[BonusSpec] = []
    potential: PotentialTemplate = Field(default_factory=PotentialTemplate)
    additional_potential: PotentialTemplate = Field(default_factory=PotentialTemplate)

    def build(self):
        generalized_gear_blueprint = self.translate_into_generalized_gear_blueprint()
        return generalized_gear_blueprint.build()

    def translate_into_generalized_gear_blueprint(
        self,
    ) -> GeneralizedGearBlueprint:

        spell_traces = []
        scrolls = []

        if self.spell_trace is not None:
            spell_traces = [
                self.spell_trace for i in range(self.meta.max_scroll_chance)
            ]
        elif self.scroll is not None:
            scrolls = [self.scroll for i in range(self.meta.max_scroll_chance)]

        starforce = Starforce(enhancement_type="Starforce", star=self.star)
        starforce.apply_star_cutoff(self.meta)

        return GeneralizedGearBlueprint(
            meta=self.meta,
            spell_traces=spell_traces,
            scrolls=scrolls,
            starforce=starforce,
            bonuses=self.bonuses,
            potential=self.potential,
            additional_potential=self.additional_potential,
        )
