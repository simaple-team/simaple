from typing import Any, Type

import pydantic

from simaple.app.domain.simulator import Simulator
from simaple.simulate.interface.simulator_configuration import (
    BaselineConfiguration,
    MinimalSimulatorConfiguration,
    SimulatorConfiguration,
)
from simaple.simulate.policy.base import Operation
from simaple.simulate.policy.parser import parse_simaple_runtime

_CONFIGURATION_TEMPLATES: dict[str, Type[SimulatorConfiguration]] = {
    "minimal_configuration": MinimalSimulatorConfiguration,
    "baseline_configuration": BaselineConfiguration,
}


class PlanMetadata(pydantic.BaseModel):
    configuration_name: str
    author: str = ""
    data: dict[str, Any]


def load_simulator(metadata: PlanMetadata) -> Simulator:
    configuration_template = _CONFIGURATION_TEMPLATES[metadata.configuration_name]
    configuration = configuration_template(**metadata.data)
    return Simulator.create_from_config(configuration)


def get_simulator_from_plan(plan_text: str) -> Simulator:
    metadata_dict, ops = parse_simaple_runtime(plan_text.strip())
    metadata = PlanMetadata.model_validate(metadata_dict)

    simulator = load_simulator(metadata)
    for op in ops:
        if not isinstance(op, Operation):
            continue

        simulator.exec(op)

    return simulator
