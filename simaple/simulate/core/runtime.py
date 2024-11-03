from typing import TypeVar

from pydantic import BaseModel

from simaple.simulate.core import Action, Entity, Event, EventCallback
from simaple.simulate.core.reducer import ReducerType
from simaple.simulate.core.store import AddressedStore, Checkpoint, Store
from simaple.simulate.core.view import ViewerType, ViewSet
from simaple.simulate.reserved_names import Tag


def _get_event_callbacks(event: Event) -> EventCallback:
    """Wrap-up relay's decision by built-in actionss
    These decisions must provided; this is "forced action"
    """
    emiited_event_action: Action = {
        "name": event["name"],
        "method": f"{event['method']}.emitted.{event['tag'] or ''}",
        "payload": event["payload"],
    }

    done_event_action: Action = {
        "name": event["name"],
        "method": f"{event['method']}.done.{event['tag'] or ''}",
        "payload": event["payload"],
    }

    return (emiited_event_action, done_event_action)


class PostActionCallback:
    """
    PostActionCallback receives "Event" and do any post-action operations.
    PostActionCallback receives viewer; this ensure callback can read every state, but cannot modify.
    """

    def __call__(
        self, event: Event, viewer: ViewerType, all_events: list[Event]
    ) -> None:
        ...


class PreviousCallback(Entity):
    events: list[EventCallback]


S = TypeVar("S", bound=Store)


def play(store: S, action: Action, reducer: ReducerType) -> tuple[S, list[Event]]:
    events: list[Event] = []
    action_queue = [action]

    previous_callbacks = store.read_entity(
        "previous_callbacks", default=PreviousCallback(events=[])
    )
    assert previous_callbacks is not None

    # Join proposed action with previous event's callback
    for emitted_callback, done_callback in previous_callbacks.events:
        action_queue = [emitted_callback] + action_queue + [done_callback]

    for target_action in action_queue:
        resolved_events = reducer(target_action, store)
        events += resolved_events

    # Save untriggered callbacks
    store.set_entity(
        "previous_callbacks",
        PreviousCallback(events=[_get_event_callbacks(event) for event in events]),
    )

    return store, events


class PlayLog(BaseModel):
    clock: float

    action: Action
    events: list[Event]
    checkpoint: Checkpoint

    def get_delay_left(self) -> float:
        delay = 0
        for event in self.events:
            if event["tag"] in (Tag.DELAY,):
                if event["payload"]["time"] > 0:
                    delay += event["payload"]["time"]

        return delay


class SimulationRuntime:
    """
    Runtime is a simple environment that handles action.
    """

    def __init__(self, store: AddressedStore, reducer: ReducerType, viewset: ViewSet):
        self._reducer: ReducerType = reducer
        self._store = store
        self._viewset = viewset
        self._previous_callbacks: list[EventCallback] = []
        self._callbacks: list[PostActionCallback] = []

    def add_callback(self, callback: PostActionCallback) -> None:
        self._callbacks.append(callback)

    def get_viewer(self) -> ViewerType:
        return self._show

    def resolve(self, action: Action) -> list[Event]:
        return self._reducer(action, self._store)

    def play(self, action: Action) -> list[Event]:
        self._store, events = play(self._store, action, self._reducer)

        for event in events:
            for handler in self._callbacks:
                handler(event, self.get_viewer(), events)

        return events

    def save(self) -> Checkpoint:
        return Checkpoint.create(self._store)

    def load(self, ckpt: Checkpoint) -> None:
        self._store = ckpt.restore()

    def _show(self, view_name: str):
        return self._viewset.show(view_name, self._store)
