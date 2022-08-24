from abc import ABCMeta, abstractmethod
from typing import List, Optional, Union

from pydantic import BaseModel, Extra, Field

from simaple.core import Stat
from simaple.gear.bonus_factory import BonusFactory, BonusSpec
from simaple.gear.gear import Gear
from simaple.gear.gear_repository import GearRepository
from simaple.gear.improvements.scroll import Scroll
from simaple.gear.improvements.spell_trace import SpellTrace
from simaple.gear.improvements.starforce import Starforce
from simaple.gear.potential import AdditionalPotential, Potential


class AbstractGearBlueprint(BaseModel, metaclass=ABCMeta):
    class Config:
        extra = Extra.forbid

    @abstractmethod
    def build(self, gear_repository: GearRepository) -> Gear:
        ...


class GeneralizedGearBlueprint(AbstractGearBlueprint):
    gear_id: int
    spell_traces: List[SpellTrace] = Field(default_factory=list)
    scrolls: List[Scroll] = Field(default_factory=list)
    starforce: Starforce
    bonuses: List[BonusSpec] = Field(default_factory=list)
    potential: Potential = Field(default_factory=Potential)
    additional_potential: AdditionalPotential = Field(
        default_factory=AdditionalPotential
    )

    def build(self, gear_repository: GearRepository) -> Gear:
        gear = gear_repository.get_by_id(self.gear_id)

        gear.potential = self.potential.copy()
        gear.additional_potential = self.additional_potential.copy()

        bonus_factory = BonusFactory()
        bonuses = [
            bonus_factory.create(bonus_type=spec.bonus_type, grade=spec.grade)
            for spec in self.bonuses
        ]

        bonus_stat = sum(
            [bonus.calculate_improvement(gear) for bonus in bonuses],
            Stat(),
        )
        # Apply spell trace and scroll.
        spell_trace_and_scoll_stat = sum(
            [
                spell_trace.calculate_improvement(gear)
                for spell_trace in self.spell_traces
            ],
            Stat(),
        ) + sum(
            [scroll.calculate_improvement(gear) for scroll in self.scrolls],
            Stat(),
        )

        gear.add_stat(spell_trace_and_scoll_stat)

        # Apply Starforce
        gear.add_stat(self.starforce.calculate_improvement(gear))

        # Apply bonus
        gear.add_stat(bonus_stat)

        return gear


class PracticalGearBlueprint(AbstractGearBlueprint):
    gear_id: Union[int, str]
    spell_trace: Optional[SpellTrace] = None
    scroll: Optional[Scroll] = None
    star: int = 0
    bonuses: List[BonusSpec] = Field(default_factory=list)
    potential: Potential = Field(default_factory=Potential)
    additional_potential: AdditionalPotential = Field(
        default_factory=AdditionalPotential
    )

    def build(self, gear_repository):
        generalized_gear_blueprint = self.translate_into_generalized_gear_blueprint(
            gear_repository
        )
        return generalized_gear_blueprint.build(gear_repository)

    def translate_into_generalized_gear_blueprint(
        self, gear_repository: GearRepository
    ) -> GeneralizedGearBlueprint:
        if isinstance(self.gear_id, str):
            gear = gear_repository.get_by_name(self.gear_id)
        else:
            gear = gear_repository.get_by_id(self.gear_id)

        spell_traces = []
        scrolls = []

        if self.spell_trace is not None:
            spell_traces = [self.spell_trace for i in range(gear.scroll_chance)]
        elif self.scroll is not None:
            scrolls = [self.scroll for i in range(gear.scroll_chance)]

        starforce = Starforce(enhancement_type="Starforce", star=self.star)
        starforce.apply_star_cutoff(gear)

        return GeneralizedGearBlueprint(
            gear_id=gear.id,
            spell_traces=spell_traces,
            scrolls=scrolls,
            starforce=starforce,
            bonuses=self.bonuses,
            potential=self.potential,
            additional_potential=self.additional_potential,
        )
