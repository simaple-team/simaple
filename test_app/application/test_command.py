import json
import os
from pathlib import Path

from simaple.app.application.command.simulator import create_simulator, run_plan
from simaple.app.domain.simulator_configuration import MinimalSimulatorConfiguration
from simaple.app.domain.uow import UnitOfWork


def test_create_simulator(uow: UnitOfWork, minimal_conf: MinimalSimulatorConfiguration):
    create_simulator(minimal_conf, uow)


def test_run_plan(uow: UnitOfWork, minimal_conf: MinimalSimulatorConfiguration):
    plan = """
CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"

CAST "미스트 이럽션 VI"
CAST "플레임 헤이즈 VI"
x4 CAST "플레임 스윕 VI"
"""

    simulator_id = create_simulator(minimal_conf, uow)

    runtime_length = run_plan(simulator_id, plan, uow)
    assert runtime_length == 12 + 1

    runtime_length = run_plan(simulator_id, plan, uow)
    assert runtime_length == 12 + 1
