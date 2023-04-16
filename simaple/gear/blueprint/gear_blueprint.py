from abc import ABCMeta, abstractmethod
from typing import List, Optional

from pydantic import BaseModel, Extra, Field, validator

from simaple.core import Stat
from simaple.gear.bonus_factory import BonusFactory, BonusType
from simaple.gear.gear import Gear, GearMeta
from simaple.gear.improvements.scroll import Scroll
from simaple.gear.improvements.spell_trace import SpellTrace
from simaple.gear.improvements.starforce import Starforce
from simaple.gear.potential import AdditionalPotential, Potential
from simaple.gear.blueprint.potential_blueprint import PotentialTemplate, template_to_potential


class AbstractGearBlueprint(BaseModel, metaclass=ABCMeta):
    class Config:
        extra = Extra.forbid

    @abstractmethod
    def build(self) -> Gear:
        ...


class BonusSpec(BaseModel):
    bonus_type: BonusType
    grade: Optional[int]
    rank: Optional[int]

    @validator("grade")
    @classmethod
    def rank_may_in_proper_range(cls, v):
        if v is not None:
            if not 1 <= v <= 7:
                raise ValueError("grade may in range 1~7")

        return v

    @validator("rank")
    @classmethod
    def rank_and_grade_may_not_given_together(cls, v, values, **kwargs):
        if "grade" in values:
            if values["grade"] is not None and v is not None:
                raise ValueError("grade and rank may not given together.")
        if v is None and values["grade"] is None:
            raise ValueError("grade or rank may given.")

        if v is not None:
            if not 1 <= v <= 7:
                raise ValueError("rank may in range 1~7")

        return v

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
    spell_traces: List[SpellTrace] = Field(default_factory=list)
    scrolls: List[Scroll] = Field(default_factory=list)
    starforce: Starforce
    bonuses: List[BonusSpec] = Field(default_factory=list)
    potential: PotentialTemplate = Field(default_factory=PotentialTemplate)
    additional_potential: PotentialTemplate = Field(default_factory=PotentialTemplate)

    def build(self) -> Gear:
        gear_stat = self.meta.base_stat.copy()

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

        gear_stat += bonus_stat

        return Gear(
            meta=self.meta,
            stat=gear_stat,
            scroll_chance=self.meta.max_scroll_chance,
            potential=template_to_potential(self.potential),
            additional_potential=template_to_potential(self.additional_potential),
        )


class PracticalGearBlueprint(AbstractGearBlueprint):
    meta: GearMeta
    spell_trace: Optional[SpellTrace] = None
    scroll: Optional[Scroll] = None
    star: int = 0
    bonuses: List[BonusSpec] = Field(default_factory=list)
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
