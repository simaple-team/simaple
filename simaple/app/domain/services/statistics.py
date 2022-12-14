from simaple.app.domain.history import History
from simaple.app.domain.workspace import Workspace


def get_damage_logs(
    history: History, workspace: Workspace
) -> tuple[list[float], list[float]]:
    x_list = []
    y_list = []

    for playlog in history:
        x_list.append(playlog.clock)
        y_list.append(playlog.get_total_damage(workspace.calculator))

    return x_list, y_list


def get_cumulative_logs(
    history: History, workspace: Workspace
) -> tuple[list[float], list[float]]:
    x_list: list[float] = []
    y_list: list[float] = []

    cumulated_damage = 0

    for playlog in history:
        x_list.append(float(playlog.clock))
        cumulated_damage += playlog.get_total_damage(workspace.calculator)
        y_list.append(cumulated_damage)

    return x_list, y_list
