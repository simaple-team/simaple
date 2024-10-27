from datetime import datetime

from simaple.container.environment_provider import EnvironmentProvider
from simaple.container.simulation import SimulationEnvironment
from simaple.request.adapter.ability_loader.adapter import NexonAPIAbilityLoader
from simaple.request.adapter.character_basic_loader.adapter import (
    NexonAPICharacterBasicLoader,
)
from simaple.request.adapter.gear_loader.adapter import NexonAPIGearLoader
from simaple.request.adapter.hyperstat_loader.adapter import NexonAPIHyperStatLoader
from simaple.request.adapter.link_skill_loader.adapter import NexonAPILinkSkillLoader
from simaple.request.adapter.propensity_loader.adapter import NexonAPIPropensityLoader
from simaple.request.adapter.skill_loader.adapter import NexonAPICharacterSkillLoader
from simaple.request.adapter.union_loader.adapter import NexonAPIUnionLoader
from simaple.request.service.environment_provider import (
    LoadedEnvironmentProviderService,
)

HOST = "https://open.api.nexon.com"


class NexonAPIEnvironmentProvider(EnvironmentProvider):
    armor: int = 300
    mob_level: int = 265
    force_advantage: float = 1.0
    v_skill_level: int = 30
    v_improvements_level: int = 60

    character_name: str
    date: str = "2024-09-19"
    token: str

    def get_simulation_environment(self) -> SimulationEnvironment:
        service = LoadedEnvironmentProviderService(
            NexonAPIAbilityLoader(
                HOST, self.token, date=datetime.strptime(self.date, "%Y-%m-%d").date()
            ),
            NexonAPIPropensityLoader(
                HOST, self.token, date=datetime.strptime(self.date, "%Y-%m-%d").date()
            ),
            NexonAPIHyperStatLoader(
                HOST, self.token, date=datetime.strptime(self.date, "%Y-%m-%d").date()
            ),
            NexonAPIUnionLoader(
                HOST, self.token, date=datetime.strptime(self.date, "%Y-%m-%d").date()
            ),
            NexonAPIGearLoader(
                HOST, self.token, date=datetime.strptime(self.date, "%Y-%m-%d").date()
            ),
            NexonAPICharacterBasicLoader(
                HOST, self.token, date=datetime.strptime(self.date, "%Y-%m-%d").date()
            ),
            NexonAPILinkSkillLoader(
                HOST, self.token, date=datetime.strptime(self.date, "%Y-%m-%d").date()
            ),
            NexonAPICharacterSkillLoader(
                HOST, self.token, date=datetime.strptime(self.date, "%Y-%m-%d").date()
            ),
        )
        character_info = service.compute_character_info(self.character_name)

        return SimulationEnvironment(
            use_doping=True,
            armor=self.armor,
            mob_level=self.mob_level,
            force_advantage=self.force_advantage,
            v_skill_level=self.v_skill_level,
            v_improvements_level=self.v_improvements_level,
            skill_levels=character_info["hexa_skill_levels"],  # may changed
            hexa_improvement_levels=character_info[
                "hexa_skill_improvements"
            ],  # may changed
            weapon_attack_power=0,  # may changed
            passive_skill_level=0,  # may changed
            combat_orders_level=0,  # may changed
            weapon_pure_attack_power=0,  # may changed
            jobtype=character_info["job_type"],
            level=character_info["level"],
            character=character_info["final_character_stat"],
        )
