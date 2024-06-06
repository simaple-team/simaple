import json
import os
from pathlib import Path

from simaple.app.application.command.simulator import create_simulator
from simaple.app.domain.simulator_configuration import MinimalSimulatorConfiguration
from simaple.app.domain.uow import UnitOfWork


def test_create_simulator(uow: UnitOfWork, minimal_conf: MinimalSimulatorConfiguration):
    create_simulator(minimal_conf, uow)
