from typing import cast

import pydantic

from simaple.core import ActionStat, ExtendedStat, JobType, Stat
from simaple.data.jobs import get_skill_profile
from simaple.data.jobs.builtin import get_builtin_strategy, get_damage_logic
from simaple.simulate.base import SimulationRuntime
from simaple.simulate.engine import OperationEngine
from simaple.simulate.kms import get_builder
from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage


def add_extended_stats(*action_stats):
    return sum(action_stats, ExtendedStat())


class FinalCharacterStat(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    stat: Stat
    action_stat: ActionStat


class SimulationEnvironment(pydantic.BaseModel):
    """
    SimulationSetting defines complete set of configuration
    to configure Simulation Engine.
    """

    model_config = pydantic.ConfigDict(extra="forbid")

    use_doping: bool = True

    armor: int = 300
    mob_level: int = 265
    force_advantage: float = 1.0

    v_skill_level: int = 30
    v_improvements_level: int = 60

    skill_levels: dict[str, int] = {}
    hexa_improvement_levels: dict[str, int] = {}

    weapon_attack_power: int = 0

    passive_skill_level: int
    combat_orders_level: int
    weapon_pure_attack_power: int

    jobtype: JobType
    level: int
    character: FinalCharacterStat


class SimulationContainer:
    def __init__(
        self,
        environment: SimulationEnvironment,
    ) -> None:
        self.environment = environment

    def damage_logic(self):
        return get_damage_logic(
            self.environment.jobtype, self.environment.combat_orders_level
        )

    def skill_profile(self):
        return get_skill_profile(self.environment.jobtype)

    def builtin_strategy(self):
        return get_builtin_strategy(self.environment.jobtype)

    def level_advantage(self):
        return LevelAdvantage().get_advantage(
            self.environment.mob_level,
            self.environment.level,
        )

    def damage_calculator(self) -> DamageCalculator:
        damage_logic = self.damage_logic()
        level_advantage = self.level_advantage()

        return DamageCalculator(
            character_spec=self.environment.character.stat,
            damage_logic=damage_logic,
            armor=self.environment.armor,
            level_advantage=level_advantage,
            force_advantage=self.environment.force_advantage,
        )

    def builder(self):
        skill_profile = self.skill_profile()

        possible_skill_names = (
            skill_profile.v_skill_names
            + skill_profile.hexa_skill_names
            + list(skill_profile.hexa_mastery.values())
        )
        for skill_name in self.environment.skill_levels:
            assert (
                skill_name in possible_skill_names
            ), f"Given explicit skill name \
passed to level: {skill_name} is not in {possible_skill_names}"

        for hexa_improvement_name in self.environment.hexa_improvement_levels:
            assert (
                hexa_improvement_name in skill_profile.hexa_improvement_names
            ), f"Given explicit \
improvement name passed to level: {hexa_improvement_name} is not in {skill_profile.hexa_improvement_names}"

        return get_builder(
            skill_profile.get_groups(),
            self.environment.skill_levels,
            skill_profile.get_filled_v_improvements(
                self.environment.v_improvements_level
            ),
            self.environment.hexa_improvement_levels,
            skill_profile.get_skill_replacements(),
            {
                "character_stat": self.environment.character.stat,
                "character_level": self.environment.level,
                "weapon_attack_power": self.environment.weapon_attack_power,
                "weapon_pure_attack_power": self.environment.weapon_pure_attack_power,
                "action_stat": self.environment.character.action_stat,
                "passive_skill_level": self.environment.passive_skill_level,
                "combat_orders_level": self.environment.combat_orders_level,
            },
        )

    def simulation_runtime(self) -> SimulationRuntime:
        builder = self.builder()
        return cast(SimulationRuntime, builder.build_simulation_runtime())

    def operation_engine(self) -> OperationEngine:
        builder = self.builder()
        return cast(OperationEngine, builder.build_operation_engine())
