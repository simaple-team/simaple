from functional import seq

from simaple.simulate.base import ViewerType
from simaple.simulate.component.view import Validity


def available(validity: Validity) -> bool:
    return validity.valid


def has_cooldown(validity: Validity) -> bool:
    return validity.cooldown_duration > 0


_utility_methods = {
    "available": available,
    "has_cooldown": has_cooldown,
    "seq": seq,
}


class SimulationProfile:
    def __init__(self, viewer: ViewerType):
        self._viewer = viewer

    def inspect(self, eval_command: str) -> str:
        debug_output = eval(
            eval_command,
            None,
            {"viewer": self._viewer, **_utility_methods},
        )

        if isinstance(debug_output, list):
            return "\n".join([str(x) for x in debug_output])

        return str(debug_output)
