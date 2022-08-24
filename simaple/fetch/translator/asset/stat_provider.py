from simaple.core import ActionStat, AnyStat, LevelStat, Stat, StatProps
from simaple.fetch.translator.potential import AbstractStatProvider


class StatProvider(AbstractStatProvider):
    target: StatProps

    def provide(self, dependency: int) -> AnyStat:
        return Stat(**{self.target.value: dependency})


class ActionStatProvider(AbstractStatProvider):
    target: str

    def provide(self, dependency: int) -> AnyStat:
        return ActionStat(**{self.target: dependency})


class LevelStatProvider(AbstractStatProvider):
    target: StatProps

    def provide(self, dependency: int) -> AnyStat:
        return LevelStat(**{self.target.value: dependency})


class AllStatProvider(AbstractStatProvider):
    def provide(self, dependency: int) -> AnyStat:
        return Stat.all_stat(dependency)


class AllStatMultiplierProvider(AbstractStatProvider):
    def provide(self, dependency: int) -> AnyStat:
        return Stat.all_stat_multiplier(dependency)


class NullStatProvider(AbstractStatProvider):
    def provide(self, dependency: int) -> AnyStat:
        return Stat()
