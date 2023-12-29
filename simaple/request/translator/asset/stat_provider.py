from simaple.core import ActionStat, ExtendedStat, LevelStat, Stat, StatProps
from simaple.request.translator.potential import AbstractStatProvider


class AllAttackProvider(AbstractStatProvider):
    def provide(self, dependency: float) -> ExtendedStat:
        return ExtendedStat(stat=Stat(attack_power=dependency, magic_attack=dependency))


class StatProvider(AbstractStatProvider):
    target: StatProps

    def provide(self, dependency: float) -> ExtendedStat:
        return ExtendedStat(stat=Stat(**{self.target.value: dependency}))


class ActionStatProvider(AbstractStatProvider):
    target: str

    def provide(self, dependency: float) -> ExtendedStat:
        return ExtendedStat(action_stat=ActionStat(**{self.target: dependency}))


class LevelStatProvider(AbstractStatProvider):
    target: StatProps

    def provide(self, dependency: float) -> ExtendedStat:
        return ExtendedStat(level_stat=LevelStat(**{self.target.value: dependency}))


class AllStatProvider(AbstractStatProvider):
    def provide(self, dependency: float) -> ExtendedStat:
        return ExtendedStat(stat=Stat.all_stat(dependency))


class AllStatMultiplierProvider(AbstractStatProvider):
    def provide(self, dependency: float) -> ExtendedStat:
        return ExtendedStat(stat=Stat.all_stat_multiplier(dependency))


class NullStatProvider(AbstractStatProvider):
    def provide(self, dependency: float) -> ExtendedStat:
        return ExtendedStat()
