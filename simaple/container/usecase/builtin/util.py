from typing import Callable

from simaple.container.simulation import SimulationEnvironment, get_skill_components
from simaple.simulate.component.base import Component


def get_component_loader(
    environment: SimulationEnvironment,
) -> Callable[[str], Component]:
    components = {skill.name: skill for skill in get_skill_components(environment)}

    def get_component(name: str) -> Component:
        return components[name]

    return get_component
