from typing import cast

from simaple.container.plan_metadata import PlanMetadata
from simaple.simulate.policy.base import ConsoleText, Operation, is_console_command
from simaple.simulate.policy.parser import parse_simaple_runtime
from simaple.wasm.base import return_js_object_from_pydantic_list
from simaple.wasm.models.simulation import OperationLogResponse


@return_js_object_from_pydantic_list
def runSimulatorWithPlanConfig(
    plan: str,
) -> list[OperationLogResponse]:
    metadata_dict, op_or_consoles = parse_simaple_runtime(plan.strip())
    metadata = PlanMetadata.model_validate(metadata_dict)

    container = metadata.load_container()
    engine = container.operation_engine()

    for op_or_console in op_or_consoles:
        if is_console_command(op_or_console):
            console_output = engine.console(cast(ConsoleText, op_or_console))
            continue

        engine.exec(cast(Operation, op_or_console))

    return [
        OperationLogResponse.from_simulator(engine, log_index)
        for log_index in range(len(engine.history()))
    ]
