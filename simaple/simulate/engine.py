from typing import Callable, Generator, Protocol, runtime_checkable

from simaple.simulate.core.base import Event
from simaple.simulate.core.reducer import ReducerType
from simaple.simulate.core.runtime import PlayLog, PostActionCallback, play
from simaple.simulate.core.store import AddressedStore, Checkpoint
from simaple.simulate.core.view import ViewerType, ViewSet
from simaple.simulate.policy.base import (
    Command,
    ConsoleText,
    Operation,
    OperationLog,
    SimulationHistory,
)
from simaple.simulate.policy.handlers import BehaviorGenerator
from simaple.simulate.profile import SimulationProfile
from simaple.simulate.report.base import SimulationEntry


@runtime_checkable
class OperationEngine(Protocol):
    def get_current_viewer(self) -> ViewerType:
        ...

    def get_buffered_events(self) -> list[Event]:
        ...

    def operation_logs(self) -> Generator[OperationLog, None, None]:
        ...

    def get_simulation_entry(self, playlog: PlayLog) -> SimulationEntry:
        ...

    def rollback(self, idx: int):
        ...

    def simulation_entries(self) -> Generator[SimulationEntry, None, None]:
        ...

    def get_viewer(self, playlog: PlayLog) -> ViewerType:
        ...

    def exec(self, command: Command) -> OperationLog:
        ...

    def reload(self, previous_operation_logs: list[OperationLog]) -> None:
        ...

    def current_index(self) -> int:
        ...


def was_no_op(logs: list[PlayLog]) -> bool:
    total_events = sum(len(playlog.events) for playlog in logs)
    return total_events == 0


class NoOpError(Exception):
    ...


class BasicOperationEngine:
    """
    OperationEngine is a simulation engine that accepts Operation for input.
    """

    def __init__(
        self,
        reducer: ReducerType,
        store: AddressedStore,
        viewset: ViewSet,
        handlers: dict[str, Callable[[Operation], BehaviorGenerator]],
    ):
        self._reducer = reducer
        self._viewset = viewset
        self._handlers = handlers

        self._buffered_events: list[Event] = []

        self._history = SimulationHistory(store)
        self._callbacks: list[PostActionCallback] = []

    def operation_logs(self) -> Generator[OperationLog, None, None]:
        for operation_log in self._history:
            yield operation_log

    def reload(self, previous_operation_logs: list[OperationLog]) -> None:
        self._history = SimulationHistory(logs=previous_operation_logs)

    def exec(self, command: Command) -> OperationLog:
        match command:
            case Operation(command_type="operation") as op:
                return self._exec_operation(op)
            case ConsoleText(command_type="console") as console:
                return self._console(console)

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

    def get_viewer(self, playlog: PlayLog) -> ViewerType:
        return self._viewset.get_viewer_from_ckpt(playlog.checkpoint)

    def simulation_entries(self) -> Generator[SimulationEntry, None, None]:
        for playlog in self._history.playlogs():
            yield self.get_simulation_entry(playlog)

    def current_index(self) -> int:
        return len(self._history) - 1

    def rollback(self, idx: int):
        self._history.discard_after(idx)

    def _console(self, console_text: ConsoleText) -> OperationLog:
        output = SimulationProfile(self.get_current_viewer()).inspect(console_text.text)
        return self._history.commit(
            console_text,
            [],
            description=output,
        )

    def _exec_operation(self, op: Operation, early_stop: int = -1) -> OperationLog:
        """
        Execute given Operation and return OperationLog.
        """
        playlogs: list[PlayLog] = []
        store = self._history.move_store()

        for behavior in self._get_behavior_gen(op):
            if 0 < early_stop <= self._viewset.show("clock", store):
                break

            action = behavior(self._buffered_events)
            if action is None:
                break

            store, self._buffered_events = play(store, action, self._reducer)

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

        if was_no_op(playlogs):
            raise NoOpError(
                f"Request no-op is forbidden. Given Operation {op} was no-op"
            )

        return self._history.commit(
            op,
            playlogs,
            description=None,
            moved_store=store,
        )


assert issubclass(BasicOperationEngine, OperationEngine)
