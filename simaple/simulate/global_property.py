from simaple.core.base import ActionStat
from simaple.simulate.base import State, Store


class Dynamics(State):
    stat: ActionStat


class Clock(State):
    current_time: float = 0.0

    def spent(self, time: float):
        self.current_time += time


class GlobalProperty:
    def __init__(self, action_stat: ActionStat):
        self._action_stat = action_stat

    def install_global_properties(self, store: Store):
        store.set_state("global.dynamics", Dynamics(stat=self._action_stat))
        store.set_state("global.time", Clock())

    @classmethod
    def get_default_binds(cls):
        return {"dynamics": "global.dynamics"}
