from abc import ABCMeta, abstractmethod

import pydantic

from simaple.core.base import ActionStat, Stat
from simaple.core.jobtype import JobType
from simaple.data.client_configuration import (
    ClientConfiguration,
    get_client_configuration,
)
from simaple.data.damage_logic import get_damage_logic
from simaple.simulate.base import Client
from simaple.simulate.kms import get_client
from simaple.simulate.report.dpm import DPMCalculator, LevelAdvantage


class SimulatorConfiguration(pydantic.BaseModel, metaclass=ABCMeta):
    class Config:
        extra = "forbid"

    @abstractmethod
    def create_client(self) -> Client:
        ...

    @abstractmethod
    def create_damage_calculator(self) -> DPMCalculator:
        ...

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        ...


class MinimalSimulatorConfiguration(SimulatorConfiguration):
    action_stat: ActionStat
    job: str

    character_stat: Stat
    character_level: int

    combat_orders_level: int = 1
    force_advantage: float = 1.5
    elemental_resistance_disadvantage: float = 0.5
    target_armor: int = 300
    mob_level: int = 250
    weapon_attack: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "minimal"

    def get_jobtype(self) -> JobType:
        return JobType(self.job)

    def get_client_configuration(self) -> ClientConfiguration:
        return get_client_configuration(self.get_jobtype())

    def create_client(self) -> Client:
        client_configuration = self.get_client_configuration()
        return get_client(
            self.action_stat,
            client_configuration.get_groups(),
            self.get_injected_values(),
            client_configuration.get_filled_v_skill(),
            client_configuration.get_filled_v_improvements(),
        )

    def get_injected_values(self) -> dict:
        return {
            "character_level": self.character_level,
            "character_stat": self.character_stat,
            "weapon_attack": self.weapon_attack,
        }

    def create_damage_calculator(self) -> DPMCalculator:
        """TODO: replace by simaple.container.simulation container-logic"""
        return DPMCalculator(
            character_spec=self.character_stat,
            damage_logic=get_damage_logic(self.get_jobtype(), self.combat_orders_level),
            armor=self.target_armor,
            level_advantage=LevelAdvantage().get_advantage(
                self.mob_level, self.character_level
            ),
            force_advantage=self.force_advantage,
            elemental_resistance_disadvantage=self.elemental_resistance_disadvantage,
        )
