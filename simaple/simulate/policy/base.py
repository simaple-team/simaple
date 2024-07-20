import hashlib
from typing import Any, Generator, Optional

from pydantic import BaseModel, PrivateAttr

from simaple.simulate.base import AddressedStore, Checkpoint, PlayLog


class Operation(BaseModel):
    """
    Operand is an aggregation of meaningful actions.
    An operand can contain one or more actions; This meant
    only operand-to-action translation is possible.
    """

    command: str
    name: str
    time: Optional[float] = None
    expr: str = ""


class OperationLog(BaseModel):
    operation: Operation
    playlogs: list[PlayLog]
    previous_hash: str
    _calculated_hash: Optional[str] = PrivateAttr(default=None)

    @property
    def hash(self) -> str:
        if not self._calculated_hash:
            stringified = self.previous_hash + self._fast_dumped_string()
            self._calculated_hash = hashlib.sha1(stringified.encode()).hexdigest()

        return self._calculated_hash

    def _fast_dumped_string(self) -> str:
        return self.operation.model_dump_json() + "|".join(
            playlog.model_dump_json(exclude=set(["checkpoint"]))
            for playlog in self.playlogs
        )

    def last(self) -> PlayLog:
        return self.playlogs[-1]


class SimulationHistory:
    def __init__(
        self,
        initial_store: Optional[AddressedStore] = None,
        logs: Optional[list[OperationLog]] = None,
    ) -> None:
        assert not (logs is None and initial_store is None)
        if initial_store:
            self._logs: list[OperationLog] = [
                OperationLog(
                    operation=Operation(command="init", name="init"),
                    playlogs=[
                        PlayLog(
                            clock=0,
                            action={"name": "init", "method": "init", "payload": None},
                            events=[],
                            checkpoint=Checkpoint.create(initial_store),
                        )
                    ],
                    previous_hash="",
                )
            ]
        else:
            assert logs is not None
            self._logs = logs

        self._cached_store: Optional[AddressedStore] = None

    def discard_after(self, idx: int) -> None:
        """Discard logs after idx."""
        self._logs = self._logs[: idx + 1]
        self._cached_store = None

    def get(self, idx: int) -> OperationLog:
        return self._logs[idx]

    def __len__(self) -> int:
        return len(self._logs)

    def __iter__(self):
        return iter(self._logs)

    def commit(
        self,
        operation: Operation,
        playlogs: list[PlayLog],
        moved_store: Optional[AddressedStore] = None,
    ) -> OperationLog:
        if len(self._logs) == 0:
            previous_hash = ""
        else:
            previous_hash = self._logs[-1].hash

        operation_log = OperationLog(
            operation=operation,
            playlogs=playlogs,
            previous_hash=previous_hash,
        )
        self._logs.append(operation_log)
        self._cached_store = moved_store

        return operation_log  # return ptr; maybe dangerous

    def playlogs(self) -> Generator[PlayLog, None, None]:
        for log in self._logs:
            for playlog in log.playlogs:
                yield playlog

    def save(self) -> dict[str, Any]:
        return {
            "logs": [log.model_dump() for log in self._logs],
        }

    def load(self, saved_history) -> None:
        self._logs = [OperationLog.parse_obj(log) for log in saved_history["logs"]]

    def current_store(self) -> AddressedStore:
        if self._cached_store is None:
            self._cached_store = self._current_ckpt().restore()

        return self._cached_store

    def move_store(self) -> AddressedStore:
        """This "moves" ownership of store to caller."""
        store = self.current_store()
        self._cached_store = None

        return store

    def shallow_copy(self) -> "SimulationHistory":
        return SimulationHistory(logs=list(self._logs))

    def show_ops(self) -> list[Operation]:
        return [playlog.operation for playlog in self]

    def get_hash_index(self, log_hash: str) -> int:
        for idx, log in enumerate(self._logs):
            if log.previous_hash == log_hash:
                return idx - 1

        if self._logs[-1].hash == log_hash:
            return len(self._logs) - 1

        raise ValueError("No matching hash")

    def _current_ckpt(self) -> Checkpoint:
        return self._logs[-1].last().checkpoint
