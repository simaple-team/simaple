from simaple.app.wasm.base import MaybePyodide, SessionlessUnitOfWork, pyodide_reveal_dict
from simaple.simulate.interface.simulator_configuration import BaselineConfiguration

from simaple.app.application.command.simulator import (
    create_simulator,
)



def createSimulatorFromBaseline(
    conf: MaybePyodide,
    uow: SessionlessUnitOfWork,
) -> str:
    baseline_conf = BaselineConfiguration.model_validate(pyodide_reveal_dict(conf))
    simulator_id = create_simulator(baseline_conf, uow)
    return simulator_id



def createSimulatorFromMinimalConf():
    ...

