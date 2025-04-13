import os

from pydantic import BaseModel

from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.container.memoizer import PersistentStorageMemoizer
from simaple.container.simulation import get_damage_calculator
from simaple.container.usecase.builtin import get_engine
from simaple.core import JobType
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.simulate.report.feature import MaximumDealingIntervalFeature


class RankingConfiguration(BaseModel):
    tier: str

    # 내실
    level: int
    artifact_level: int
    union_block_count: int
    link_count: int = 12 + 1
    propensity_level: int = 100

    # skill levels
    v_skill_level: int
    v_improvements_level: int
    hexa_improvements_level: int
    passive_skill_level: int
    combat_orders_level: int

    # enemy configuration
    armor: int = 300
    mob_level: int = 265
    force_advantage: float = 1.0

    # weapon configuration (not used in this phase)
    weapon_pure_attack_power: int = 0
    weapon_attack_power: int = 0

    plan_root_path: str
    cache_root_path: str

    def get_environment_provider(self, jobtype: JobType) -> BaselineEnvironmentProvider:
        return BaselineEnvironmentProvider(
            tier=self.tier,
            level=self.level,
            artifact_level=self.artifact_level,
            union_block_count=self.union_block_count,
            link_count=self.link_count,
            propensity_level=self.propensity_level,
            v_skill_level=self.v_skill_level,
            v_improvements_level=self.v_improvements_level,
            hexa_improvements_level=self.hexa_improvements_level,
            passive_skill_level=self.passive_skill_level,
            combat_orders_level=self.combat_orders_level,
            jobtype=jobtype,
            armor=self.armor,
            mob_level=self.mob_level,
            force_advantage=self.force_advantage,
            weapon_pure_attack_power=self.weapon_pure_attack_power,
            weapon_attack_power=self.weapon_attack_power,
        )


def run_actor(configuration: RankingConfiguration, jobtype: JobType):
    environment_provider = configuration.get_environment_provider(jobtype)

    environment = PersistentStorageMemoizer(
        os.path.join(configuration.cache_root_path, ".memo.simaple.json")
    ).compute_environment(environment_provider)

    engine = get_engine(environment)

    with open(
        os.path.join(
            configuration.plan_root_path, f"{environment.jobtype.value}.simaple"
        ),
        "r",
    ) as f:
        _, commands = parse_simaple_runtime(f.read())

    for command in commands:
        engine.exec(command)

    report = list(engine.simulation_entries())
    damage_calculator = get_damage_calculator(environment)

    return report, damage_calculator


def rank_between_jobs(
    targets: list[JobType],
    configuration: RankingConfiguration,
    interval: int,
) -> None:
    dealing: dict[JobType, float] = {}

    for jobtype in targets:
        report, damage_calculator = run_actor(configuration, jobtype)

        feature = MaximumDealingIntervalFeature(interval=interval)
        best_dealing, best_start, best_end = feature.find_maximum_dealing_interval(
            report, damage_calculator
        )
        print(f"best_start: {best_start}, best_end: {best_end}")

        print(f"dpm: {damage_calculator.calculate_dpm(report):,}")
        dealing[jobtype] = damage_calculator.calculate_dpm(report)

    # sort by dealing
    sorted_dealing = sorted(dealing.items(), key=lambda x: x[1], reverse=True)

    for ranked_jobtype, ranked_dealing in sorted_dealing:
        print(f"{ranked_jobtype}: {ranked_dealing:,}")
