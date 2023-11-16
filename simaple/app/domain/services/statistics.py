from simaple.app.domain.simulator import Simulator
from simaple.simulate.policy.base import PlayLog, SimulationHistory, SimulationShell


def get_damage_logs(
    shell: SimulationShell, simulator: Simulator
) -> tuple[list[float], list[float]]:
    x_list = []
    y_list = []

    for playlog in shell._history.playlogs():
        report = shell.get_report(playlog)
        x_list.append(playlog.clock)
        y_list.append(simulator.calculator.calculate_damage(report))

    return x_list, y_list


def get_cumulative_logs(
    shell: SimulationShell, simulator: Simulator
) -> tuple[list[float], list[float]]:
    x_list: list[float] = []
    y_list: list[float] = []

    cumulated_damage = 0

    for playlog in shell._history.playlogs():
        report = shell.get_report(playlog)
        x_list.append(float(playlog.clock))
        cumulated_damage += simulator.calculator.calculate_damage(report)
        y_list.append(cumulated_damage)

    return x_list, y_list
