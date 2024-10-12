from simaple.simulate.base import Event, Store, Action, ConcreteStore

from simaple.simulate.reducer import wildcard_and_listening_action_reducer

import pytest

@pytest.fixture
def sample_store() -> Store:
    return ConcreteStore()


@pytest.fixture
def sample_reducer(store: Store, action: Action) -> list[Event]:
    if action["name"] != "sample_reducer":
        return []

    return [{
        "method": "A",
        "name": "sample_reducer",
        "payload": {},
        "handler": None,
        "tag": None
    }]



def test_listening_action_reducer(sample_store, sample_reducer):
    new_reducer = wildcard_and_listening_action_reducer(
        "P", {
            "listening_action": "sample_reducer",
        }
    )(sample_reducer)

    assert new_reducer(sample_store, {"name": "A"}) == []
    assert new_reducer(sample_store, {"name": "sample_reducer"}) == [{
        "method": "A",
        "name": "sample_reducer",
        "payload": {},
        "handler": None,
        "tag": None
    }]




