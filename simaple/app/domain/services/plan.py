from typing import Any, Type

import pydantic

from simaple.app.domain.simulator import Simulator
from simaple.app.domain.snapshot import PlanMetadata
from simaple.container.simulation import SimulationSetting
from simaple.simulate.policy.base import Operation
from simaple.simulate.policy.parser import parse_simaple_runtime


def get_simulator_from_plan(plan_text: str) -> Simulator:
    metadata_dict, ops = parse_simaple_runtime(plan_text.strip())
    metadata = PlanMetadata.model_validate(metadata_dict)

    simulator = metadata.load_simulator()
    for op in ops:
        if not isinstance(op, Operation):
            continue

        simulator.exec(op)

    return simulator
