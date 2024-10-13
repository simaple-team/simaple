import pytest

from simaple.simulate.component.base import StaticPayloadReducerInfo
from simaple.simulate.core.base import Action, Event
from simaple.simulate.core.store import ConcreteStore, Store
from simaple.simulate.reducer import wildcard_and_listening_action_reducer


@pytest.fixture
def sample_store() -> Store:
    return ConcreteStore()


def sample_reducer(
    action: Action,
    store: Store,
) -> list[Event]:
    if action["method"] != "sample_method":
        return []

    return [
        {
            "method": "sample_method",
            "name": "A",
            "payload": {},
            "handler": None,
            "tag": None,
        }
    ]


def test_listening_action_reducer(sample_store):
    new_reducer = wildcard_and_listening_action_reducer(
        "P",
        {
            "A.listening_method": "sample_method",
            "A.listen_with_payload": StaticPayloadReducerInfo.model_validate(
                {"name": "sample_method", "payload": {}}
            ),
        },
    )(sample_reducer)

    assert (
        new_reducer(
            {
                "name": "A",
                "method": "??",
                "payload": {},
            },
            sample_store,
        )
        == []
    )

    assert new_reducer(
        {
            "name": "A",
            "method": "sample_method",
            "payload": {},
        },
        sample_store,
    ) == [
        {
            "method": "sample_method",
            "name": "A",
            "payload": {},
            "handler": None,
            "tag": None,
        }
    ]

    assert new_reducer(
        {
            "name": "A",
            "method": "listening_method",
            "payload": {},
        },
        sample_store,
    ) == [
        {
            "method": "sample_method",
            "name": "A",
            "payload": {},
            "handler": None,
            "tag": None,
        }
    ]

    assert new_reducer(
        {
            "name": "A",
            "method": "listen_with_payload",
            "payload": {},
        },
        sample_store,
    ) == [
        {
            "method": "sample_method",
            "name": "A",
            "payload": {},
            "handler": None,
            "tag": None,
        }
    ]
