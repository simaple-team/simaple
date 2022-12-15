from simaple.app.application.exception import UnknownWorkspaceException
from simaple.app.domain.history import History
from simaple.app.domain.services.workspace_builder import WorkspaceConfiguration
from simaple.app.domain.uow import UnitOfWork
from simaple.simulate.base import Action


def create_workspace(conf: WorkspaceConfiguration, uow: UnitOfWork) -> str:
    workspace = conf.create_workspace()

    playlog = workspace.empty_action_playlog()
    history = History(id=workspace.id, logs=[playlog])

    uow.workspace_repository().add(workspace)
    uow.history_repository().add(history)

    return workspace.id


def play_action(workspace_id: str, action: Action, uow: UnitOfWork) -> None:
    workspace = uow.workspace_repository().get(workspace_id)
    history = uow.history_repository().get(workspace_id)

    if history is None or workspace is None:
        raise UnknownWorkspaceException()

    playlog = workspace.dispatch(action)
    history.append(playlog)

    uow.history_repository().update(history)
    uow.workspace_repository().update(workspace)


def play_use(workspace_id: str, name: str, uow: UnitOfWork) -> None:
    workspace = uow.workspace_repository().get(workspace_id)
    history = uow.history_repository().get(workspace_id)

    if history is None or workspace is None:
        raise UnknownWorkspaceException()

    playlog = workspace.dispatch(Action(name=name, method="use", payload=None))
    history.append(playlog)

    uow.history_repository().update(history)
    uow.workspace_repository().update(workspace)


def play_elapse(workspace_id: str, time: float, uow: UnitOfWork) -> None:
    workspace = uow.workspace_repository().get(workspace_id)
    history = uow.history_repository().get(workspace_id)

    if history is None or workspace is None:
        raise UnknownWorkspaceException()

    playlog = workspace.dispatch(
        Action(
            name="*",
            method="elapse",
            payload=time,
        )
    )
    history.append(playlog)

    uow.history_repository().update(history)
    uow.workspace_repository().update(workspace)


def play_use_and_elapse(workspace_id: str, name: str, uow: UnitOfWork) -> None:
    workspace = uow.workspace_repository().get(workspace_id)
    history = uow.history_repository().get(workspace_id)

    if history is None or workspace is None:
        raise UnknownWorkspaceException()

    playlog = workspace.dispatch(Action(name=name, method="use", payload=None))
    history.append(playlog)

    playlog = workspace.dispatch(
        Action(name="*", method="elapse", payload=playlog.get_delay())
    )
    history.append(playlog)

    uow.history_repository().update(history)
    uow.workspace_repository().update(workspace)
