import uuid
from typing import Any

import pydantic

from simaple.app.domain.workspace import Workspace
from simaple.core.base import ActionStat, Stat
from simaple.core.damage import INTBasedDamageLogic
from simaple.simulate.base import Client
from simaple.simulate.kms import get_client
from simaple.simulate.report.dpm import DPMCalculator, LevelAdvantage


class WorkspaceConfiguration(pydantic.BaseModel):
    action_stat: ActionStat
    groups: list[str]
    injected_values: dict[str, Any]
    skill_levels: dict[str, int]
    v_improvements: dict[str, int]
    character_stat: Stat

    def create_workspace(self) -> Workspace:
        return Workspace(
            id=str(uuid.uuid4()),
            client=self.create_client(),
            calculator=self.create_damage_calculator(),
        )

    def create_client(self) -> Client:
        return get_client(
            self.action_stat,
            self.groups,
            self.injected_values,
            self.skill_levels,
            self.v_improvements,
        )

    def create_damage_calculator(self) -> DPMCalculator:
        """TODO: replace by simaple.container.simulation container-logic"""
        return DPMCalculator(
            character_spec=self.character_stat,
            damage_logic=INTBasedDamageLogic(attack_range_constant=1.2, mastery=0.95),
            armor=300,
            level_advantage=LevelAdvantage().get_advantage(250, 260),
            force_advantage=1.5,
            elemental_resistance_disadvantage=0.5,
        )
