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


class SimulationSetting(pydantic.BaseModel):
    """
    SimulationSetting defines complete set of configuration
    to configure Simulation Engine.
    """

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

    passive_skill_level: int
    combat_orders_level: int
    weapon_pure_attack_power: int

    jobtype: JobType
    level: int
    character: ExtendedStat


class SimulationContainer:
    def __init__(
        self,
        setting: SimulationSetting,
    ) -> None:
        self.setting = setting

    def damage_logic(self):
        return get_damage_logic(self.setting.jobtype, self.setting.combat_orders_level)

    def skill_profile(self):
        return get_skill_profile(self.setting.jobtype)

    def builtin_strategy(self):
        return get_builtin_strategy(self.setting.jobtype)

    def level_advantage(self):
        return LevelAdvantage().get_advantage(
            self.setting.mob_level,
            self.setting.level,
        )

    def damage_calculator(self) -> DamageCalculator:
        damage_logic = self.damage_logic()
        level_advantage = self.level_advantage()

        return DamageCalculator(
            character_spec=self.setting.character.stat,
            damage_logic=damage_logic,
            armor=self.setting.armor,
            level_advantage=level_advantage,
            force_advantage=self.setting.force_advantage,
        )

    def builder(self):
        skill_profile = self.skill_profile()

        return get_builder(
            skill_profile.get_groups(),
            skill_profile.get_skill_levels(
                self.setting.v_skill_level,
                self.setting.hexa_skill_level,
                self.setting.hexa_mastery_level,
            ),
            skill_profile.get_filled_v_improvements(self.setting.v_improvements_level),
            skill_profile.get_filled_hexa_improvements(
                self.setting.hexa_improvements_level
            ),
            skill_profile.get_skill_replacements(),
            {
                "character_stat": self.setting.character.stat,
                "character_level": self.setting.level,
                "weapon_attack_power": self.setting.weapon_attack_power,
                "weapon_pure_attack_power": self.setting.weapon_pure_attack_power,
                "action_stat": self.setting.character.action_stat,
                "passive_skill_level": self.setting.passive_skill_level,
                "combat_orders_level": self.setting.combat_orders_level,
            },
        )

    def simulation_runtime(self) -> SimulationRuntime:
        builder = self.builder()
        return cast(SimulationRuntime, builder.build_simulation_runtime())

    def operation_engine(self) -> OperationEngine:
        builder = self.builder()
        return cast(OperationEngine, builder.build_operation_engine())
