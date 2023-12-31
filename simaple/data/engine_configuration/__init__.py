from pathlib import Path
from typing import cast

import pydantic

from simaple.core import JobType, ActionStat
from simaple.simulate.policy.base import PolicyWrapper
from simaple.simulate.policy.default import normal_default_ordered_policy
from simaple.spec.loadable import (  # pylint:disable=unused-import
    TaggedNamespacedABCMeta,
)
from simaple.spec.loader import SpecBasedLoader
from simaple.spec.repository import DirectorySpecRepository


class EngineConfiguration(
    pydantic.BaseModel, metaclass=TaggedNamespacedABCMeta(kind="EngineConfiguration")
):
    """
    EngineConfiguration
    A pre-assigned information to create specific job's components easier
    """

    v_skill_names: list[str]
    v_improvement_names: list[str]
    component_groups: list[str]
    mdc_order: list[str]
    hexa_skill_names: list[str] = pydantic.Field(default=[])
    hexa_mastery: dict[str, str] = pydantic.Field(default={})

    def get_filled_v_skill(self, level: int = 30) -> dict[str, int]:
        return {k: level for k in self.v_skill_names}

    def get_skill_levels(self, v_level: int, hexa_level: int) -> dict[str, int]:
        skill_levels = {}
        skill_levels.update(self.get_filled_v_skill(v_level))
        skill_levels.update(self.get_filled_hexa_skill(hexa_level))
        return skill_levels

    def get_filled_hexa_skill(self, level: int) -> dict[str, int]:
        """
        TODO: refactor skill level injection strategy
        """
        return {k: level for k in self.hexa_skill_names}

    def get_filled_v_improvements(self, level: int = 60) -> dict[str, int]:
        return {k: level for k in self.v_improvement_names}

    def get_groups(self) -> list[str]:
        return self.component_groups

    def get_default_policy(self):
        return PolicyWrapper(normal_default_ordered_policy(order=self.mdc_order))

    def get_engine_builder(
            self, 
            action_stat: ActionStat, 
            combat_orders_level: int,
            passive_skill_level: int,
        ):

        ...


def get_engine_configuration(jobtype: JobType) -> EngineConfiguration:
    repository = DirectorySpecRepository(str(Path(__file__).parent / "resources"))
    loader = SpecBasedLoader(repository)
    return cast(
        EngineConfiguration,
        loader.load(
            query={"group": jobtype.value, "kind": "EngineConfiguration"},
        ),
    )
