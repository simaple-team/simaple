from abc import ABCMeta, abstractmethod
from typing import cast

import pydantic

from simaple.core import ExtendedStat, JobType
from simaple.data.jobs import get_skill_profile
from simaple.data.jobs.builtin import get_builtin_strategy, get_damage_logic
from simaple.simulate.base import SimulationRuntime
from simaple.simulate.engine import OperationEngine
from simaple.simulate.kms import get_builder
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage


def add_extended_stats(*action_stats):
    return sum(action_stats, ExtendedStat())


class CharacterDependentEnvironment(pydantic.BaseModel):
    passive_skill_level: int
    combat_orders_level: int
    weapon_pure_attack_power: int

    jobtype: JobType
    level: int

    def damage_logic(self):
        return get_damage_logic(self.jobtype, self.combat_orders_level)


class CharacterProvider(pydantic.BaseModel, metaclass=ABCMeta):
    @abstractmethod
    def character(self) -> ExtendedStat: ...

    @abstractmethod
    def get_character_dependent_simulation_config(
        self,
    ) -> CharacterDependentEnvironment: ...

    @classmethod
    def get_name(cls):
        return cls.__name__


class SimulationEnvironment(pydantic.BaseModel):
    use_doping: bool = True

    armor: int = 300
    mob_level: int = 265
    force_advantage: float = 1.0

    v_skill_level: int = 30
    hexa_skill_level: int = 1
    hexa_mastery_level: int = 1
    v_improvements_level: int = 60
    hexa_improvements_level: int = 0

    weapon_attack_power: int = 0


class SimulationSetting(pydantic.BaseModel):
    """
    SimulationSetting defines complete set of configuration
    to configure Simulation Engine.
    """
    environment: SimulationEnvironment
    character: ExtendedStat
    character_dependent_environment: CharacterDependentEnvironment


class SimulationContainer:
    def __init__(
        self,
        setting: SimulationSetting,
    ) -> None:
        self.setting = setting

    @classmethod
    def from_character_provider(
        cls, environment: SimulationEnvironment, character_provider: CharacterProvider
    ) -> "SimulationContainer":
        setting = SimulationSetting(
            environment=environment,
            character=character_provider.character(),
            character_dependent_environment=character_provider.get_character_dependent_simulation_config(),
        )
        return cls(setting)

    def skill_profile(self):
        return get_skill_profile(self.setting.character_dependent_environment.jobtype)

    def builtin_strategy(self):
        return get_builtin_strategy(
            self.setting.character_dependent_environment.jobtype
        )

    def level_advantage(self):
        config = self.setting
        return LevelAdvantage().get_advantage(
            config.environment.mob_level,
            self.setting.character_dependent_environment.level,
        )

    def damage_calculator(self) -> DamageCalculator:
        config = self.setting

        character = self.setting.character
        damage_logic = self.setting.character_dependent_environment.damage_logic()
        level_advantage = self.level_advantage()

        return DamageCalculator(
            character_spec=character.stat,
            damage_logic=damage_logic,
            armor=config.environment.armor,
            level_advantage=level_advantage,
            force_advantage=config.environment.force_advantage,
        )

    def builder(self):
        skill_profile = self.skill_profile()
        config = self.setting
        character = self.setting.character
        character_dependent_simulation_setting = (
            self.setting.character_dependent_environment
        )

        return get_builder(
            skill_profile.get_groups(),
            skill_profile.get_skill_levels(
                config.environment.v_skill_level,
                config.environment.hexa_skill_level,
                config.environment.hexa_mastery_level,
            ),
            skill_profile.get_filled_v_improvements(
                config.environment.v_improvements_level
            ),
            skill_profile.get_filled_hexa_improvements(
                config.environment.hexa_improvements_level
            ),
            skill_profile.get_skill_replacements(),
            {
                "character_stat": character.stat,
                "character_level": character_dependent_simulation_setting.level,
                "weapon_attack_power": config.environment.weapon_attack_power,
                "weapon_pure_attack_power": character_dependent_simulation_setting.weapon_pure_attack_power,
                "action_stat": character.action_stat,
                "passive_skill_level": character_dependent_simulation_setting.passive_skill_level,
                "combat_orders_level": character_dependent_simulation_setting.combat_orders_level,
            },
        )

    def simulation_runtime(self) -> SimulationRuntime:
        builder = self.builder()
        return cast(SimulationRuntime, builder.build_simulation_runtime())

    def operation_engine(self) -> OperationEngine:
        builder = self.builder()
        return cast(OperationEngine, builder.build_operation_engine())
