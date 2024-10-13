from simaple.simulate.core.base import (
    Action,
    AddressedStore,
    Checkpoint,
    Event,
    EventCallback,
    PostActionCallback,
    ReducerType,
    ViewerType,
    ViewSet,
    play,
)


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
