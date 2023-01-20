from abc import ABCMeta, abstractmethod

import pydantic

from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core.base import ActionStat, Stat
from simaple.core.jobtype import JobType
from simaple.data.client_configuration import (
    ClientConfiguration,
    get_client_configuration,
)
from simaple.data.damage_logic import get_damage_logic
from simaple.simulate.base import Client
from simaple.simulate.kms import get_client
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage


class SimulatorConfiguration(pydantic.BaseModel, metaclass=ABCMeta):
    class Config:
        extra = "forbid"

    @abstractmethod
    def create_client(self) -> Client:
        ...

    @abstractmethod
    def create_damage_calculator(self) -> DamageCalculator:
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
    target_armor: int = 300
    mob_level: int = 250
    weapon_attack_power: int = 0
    weapon_pure_attack_power: int = 0

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
            "weapon_attack_power": self.weapon_pure_attack_power,
            "weapon_pure_attack_power": self.weapon_pure_attack_power,
        }

    def create_damage_calculator(self) -> DamageCalculator:
        """TODO: replace by simaple.container.simulation container-logic"""
        return DamageCalculator(
            character_spec=self.character_stat,
            damage_logic=get_damage_logic(self.get_jobtype(), self.combat_orders_level),
            armor=self.target_armor,
            level_advantage=LevelAdvantage().get_advantage(
                self.mob_level, self.character_level
            ),
            force_advantage=self.force_advantage,
        )


class BaselineConfiguration(SimulatorConfiguration):
    simulation_setting: SimulationSetting

    def get_container(self) -> SimulationContainer:
        container = SimulationContainer()
        container.config.from_pydantic(self.simulation_setting)
        return container

    def create_client(self) -> Client:
        return self.get_container().client()

    def create_damage_calculator(self) -> DamageCalculator:
        return self.get_container().dpm_calculator()

    @classmethod
    def get_name(cls) -> str:
        return "baseline"
