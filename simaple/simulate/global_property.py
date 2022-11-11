from simaple.core.base import ActionStat
from simaple.simulate.base import State, Store


class Dynamics(State):
    stat: ActionStat


class GlobalProperty:
    def __init__(self, action_stat: ActionStat):
        self._action_stat = action_stat

    def install_global_properties(self, store: Store):
        store.set_state("global.dynamics", Dynamics(stat=self._action_stat))

    @classmethod
    def get_default_binds(cls):
        return {"dynamics": "global.dynamics"}
