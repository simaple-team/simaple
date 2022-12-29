from simaple.core.base import ActionStat
from simaple.simulate.base import Entity, Store


class Dynamics(Entity):
    stat: ActionStat


class Clock(Entity):
    current_time: float = 0.0

    def spent(self, time: float):
        self.current_time += time


class GlobalProperty:
    def __init__(self, action_stat: ActionStat):
        self._action_stat = action_stat

    def install_global_properties(self, store: Store):
        store.set_entity("global.dynamics", Dynamics(stat=self._action_stat))
        store.set_entity("global.time", Clock())

    @classmethod
    def get_default_binds(cls):
        return {"dynamics": "global.dynamics"}
