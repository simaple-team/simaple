from simaple.app.domain.simulator import Simulator
from simaple.app.domain.snapshot import Snapshot


def test_snapshot(sample_simulator: Simulator):
    snapshot = Snapshot.create_from_simluator("test-snapshot", sample_simulator)

    restored_simulator = snapshot.restore_simulator()

    assert (
        sample_simulator.client.environment._store.save()
        == restored_simulator.client.environment._store.save()
    )
