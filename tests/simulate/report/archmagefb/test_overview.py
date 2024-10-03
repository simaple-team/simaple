import simaple.simulate.component.common  # noqa: F401
from simaple.core.base import Stat
from simaple.simulate.base import Action, SimulationRuntime, message_signature
from simaple.simulate.reserved_names import Tag


def test_buff_view(archmagefb_simulation_runtime: SimulationRuntime):
    current_buff_stat = archmagefb_simulation_runtime.get_viewer()("buff")

    archmagefb_simulation_runtime.play(
        dict(name="에픽 어드벤쳐", method="use", payload=None)
    )

    assert archmagefb_simulation_runtime.get_viewer()(
        "buff"
    ) == current_buff_stat + Stat(damage_multiplier=10)


def test_poison_nova(archmagefb_simulation_runtime: SimulationRuntime):
    actions: list[Action] = [
        dict(name="포이즌 노바", method="use", payload=None),
        dict(name="*", method="elapse", payload=2000),
        dict(name="미스트 이럽션", method="use", payload=None),
    ]

    events = []

    for action in actions:
        events += archmagefb_simulation_runtime.play(action)

    assert "포이즌 노바.trigger" in [message_signature(e) for e in events]


def test_poison_chain(archmagefb_simulation_runtime: SimulationRuntime):
    actions: list[Action] = [
        dict(name="포이즌 체인", method="use", payload=None),
        dict(name="*", method="elapse", payload=25000),
        dict(name="*", method="elapse", payload=25000),
    ]

    events = []

    for action in actions:
        events += archmagefb_simulation_runtime.play(action)

    damage_events = [e for e in events if e["tag"] == Tag.DAMAGE]

    assert len(damage_events) == 9 + 1

    for idx in range(1, 5):
        assert (
            damage_events[idx + 1]["payload"]["damage"]
            > damage_events[idx]["payload"]["damage"]
        )
