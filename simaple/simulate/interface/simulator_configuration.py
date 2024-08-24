from abc import ABCMeta, abstractmethod

import pydantic

from simaple.container.simulation import SimulationContainer, SimulationSetting
from simaple.core.base import ActionStat, Stat
from simaple.core.jobtype import JobType
from simaple.data.damage_logic import get_damage_logic
from simaple.data.skill_profile import SkillProfile, get_skill_profile
from simaple.simulate.builder import EngineBuilder
from simaple.simulate.engine import MonotonicEngine, OperationEngine
from simaple.simulate.kms import BuilderRequiredExtraVariables, get_builder
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage


class SimulatorConfiguration(pydantic.BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def create_damage_calculator(self) -> DamageCalculator: ...

    @classmethod
    @abstractmethod
    def get_name(cls) -> str: ...

    @abstractmethod
    def create_monotonic_engine(self) -> MonotonicEngine: ...

    @abstractmethod
    def create_operation_engine(self) -> OperationEngine: ...


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

    def get_skill_profile(self) -> SkillProfile:
        return get_skill_profile(self.get_jobtype())

    def _get_builder(self) -> EngineBuilder:
        skill_profile = self.get_skill_profile()
        return get_builder(
            skill_profile.get_groups(),
            skill_profile.get_skill_levels(30, 1, 1),
            skill_profile.get_filled_v_improvements(),
            skill_profile.get_filled_hexa_improvements(),
            skill_profile.get_skill_replacements(),
            self.get_injected_values(),
        )

    def create_monotonic_engine(self) -> MonotonicEngine:
        return self._get_builder().build_monotonic_engine()

    def create_operation_engine(self) -> OperationEngine:
        return self._get_builder().build_operation_engine()

    def get_injected_values(self) -> BuilderRequiredExtraVariables:
        return {
            "character_level": self.character_level,
            "character_stat": self.character_stat,
            "weapon_attack_power": self.weapon_pure_attack_power,
            "weapon_pure_attack_power": self.weapon_pure_attack_power,
            "action_stat": self.action_stat,
            "combat_orders_level": self.combat_orders_level,
            "passive_skill_level": 0,
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
        container = SimulationContainer(self.simulation_setting)
        return container

    def create_monotonic_engine(self) -> MonotonicEngine:
        return self.get_container().monotonic_engine()

    def create_operation_engine(self) -> OperationEngine:
        return self.get_container().operation_engine()

    def create_damage_calculator(self) -> DamageCalculator:
        return self.get_container().dpm_calculator()

    @classmethod
    def get_name(cls) -> str:
        return "baseline"
