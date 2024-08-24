from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Generator, Protocol

from simaple.simulate.base import (
    Action,
    AddressedStore,
    Checkpoint,
    Event,
    EventCallback,
    PlayLog,
    PostActionCallback,
    RouterDispatcher,
    ViewerType,
    ViewSet,
    play,
)
from simaple.simulate.policy.base import Operation, OperationLog, SimulationHistory
from simaple.simulate.policy.handlers import BehaviorGenerator
from simaple.simulate.profile import SimulationProfile
from simaple.simulate.report.base import Report, SimulationEntry


class SimulationEngine(metaclass=ABCMeta):
    @abstractmethod
    def add_callback(self, callback: PostActionCallback) -> None:
        """Simulation Engine may ensure that given engine triggers registered callbacks."""


class MonotonicEngineProtocol(Protocol):
    def add_callback(self, callback: PostActionCallback) -> None: ...

    def get_viewer(self) -> ViewerType: ...


class OperationEngineProtocol(Protocol):
    def add_callback(self, callback: PostActionCallback) -> None: ...

    def get_current_viewer(self) -> ViewerType: ...

    def exec(self, op: Operation, early_stop: int = -1) -> OperationLog: ...

    def get_buffered_events(self) -> list[Event]: ...

    def create_full_report(self) -> Report: ...

    def operation_logs(self) -> Generator[OperationLog, None, None]: ...


class MonotonicEngine(SimulationEngine):
    """
    MonotonicEngine is a simulation engine that accepts bare Action.
    """

    def __init__(
        self, store: AddressedStore, router: RouterDispatcher, viewset: ViewSet
    ):
        self._router: RouterDispatcher = router
        self._store = store
        self._viewset = viewset
        self._previous_callbacks: list[EventCallback] = []
        self._callbacks: list[PostActionCallback] = []

    def add_callback(self, callback: PostActionCallback) -> None:
        self._callbacks.append(callback)

    def get_viewer(self) -> ViewerType:
        return self._show

    def resolve(self, action: Action) -> list[Event]:
        return self._router(action, self._store)

    def play(self, action: Action) -> list[Event]:
        self._store, events = play(self._store, action, self._router)

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


class OperationEngine(SimulationEngine):
    """
    OperationEngine is a simulation engine that accepts Operation for input.
    """

    def __init__(
        self,
        router: RouterDispatcher,
        store: AddressedStore,
        viewset: ViewSet,
        handlers: dict[str, Callable[[Operation], BehaviorGenerator]],
    ):
        self._router = router
        self._viewset = viewset
        self._handlers = handlers

        self._buffered_events: list[Event] = []

        self._history = SimulationHistory(store)
        self._callbacks: list[PostActionCallback] = []

    def inspect(self, log: OperationLog) -> list[tuple[PlayLog, ViewerType]]:
        return [
            (playlog, self._viewset.get_viewer_from_ckpt(playlog.checkpoint))
            for playlog in log.playlogs
        ]

    def add_callback(self, callback: PostActionCallback) -> None:
        self._callbacks.append(callback)

    def save_history(self) -> dict[str, Any]:
        return self._history.save()

    def operation_logs(self) -> Generator[OperationLog, None, None]:
        for operation_log in self._history:
            yield operation_log

    def length(self) -> int:
        return len(self._history)

    def history(self) -> SimulationHistory:
        """This returns "Shallow Copy" of SimulationHistory.
        Be cautious not to modify the returned SimulationHistory.
        Use this only for read.
        """
        return self._history.shallow_copy()

    def load_history(self, saved_history: dict[str, Any]) -> None:
        self._history.load(saved_history)

    def exec(self, op: Operation, early_stop: int = -1) -> OperationLog:
        playlogs: list[PlayLog] = []
        store = self._history.move_store()

        for behavior in self._get_behavior_gen(op):
            if 0 < early_stop <= self._viewset.show("clock", store):
                break

            action = behavior(self._buffered_events)
            if action is None:
                break

            store, self._buffered_events = play(store, action, self._router)

            playlogs.append(
                PlayLog(
                    clock=self._viewset.show("clock", store),
                    action=action,
                    events=self._buffered_events,
                    checkpoint=Checkpoint(store_ckpt=store.save()),
                )
            )

            for event in self._buffered_events:
                for handler in self._callbacks:
                    handler(
                        event,
                        self._viewset.get_viewer(store),
                        self._buffered_events,
                    )

        return self._history.commit(
            op,
            playlogs,
            moved_store=store,
        )

    def _get_behavior_gen(self, op: Operation) -> BehaviorGenerator:
        return self._handlers[op.command](op)

    def get_buffered_events(self) -> list[Event]:
        """
        Returns buffered event stored in engine.
        This return value is read-only; thus wrap internal variable with list().
        """
        return list(self._buffered_events)

    def get_current_viewer(self) -> ViewerType:
        store = self._history.current_store()
        return self._viewset.get_viewer(store)

    def get_simulation_entry(self, playlog: PlayLog) -> SimulationEntry:
        viewer = self._viewset.get_viewer_from_ckpt(playlog.checkpoint)
        buff = viewer("buff")
        return SimulationEntry.build(playlog, buff)

    def create_full_report(self) -> Report:
        report = Report()

        for operation_log in self._history:
            for playlog in operation_log.playlogs:
                report.add(self.get_simulation_entry(playlog))

        return report

    def rollback(self, idx: int):
        self._history.discard_after(idx)

    def console(self, console_text: str):
        output = SimulationProfile(self.get_current_viewer()).inspect(console_text)
        return output
