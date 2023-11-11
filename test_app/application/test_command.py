import json
import os
from pathlib import Path

from simaple.app.application.command import create_simulator, override_checkpoint
from simaple.app.domain.simulator_configuration import MinimalSimulatorConfiguration
from simaple.app.domain.uow import UnitOfWork


def test_create_simulator(uow: UnitOfWork, minimal_conf: MinimalSimulatorConfiguration):
    create_simulator(minimal_conf, uow)


def test_query_all_snapshot(
    uow: UnitOfWork, minimal_conf: MinimalSimulatorConfiguration
):
    simulator_id = create_simulator(minimal_conf, uow)

    with open(
        Path(os.path.dirname(__file__)) / "checkpoint.json", encoding="utf-8"
    ) as f:
        ckpt = json.load(f)

    override_checkpoint(simulator_id, {"store_ckpt": ckpt, "callbacks": []}, uow)
