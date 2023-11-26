from simaple.app.domain.simulator import Simulator
from simaple.simulate.engine import OperationEngine


def get_damage_logs(
    engine: OperationEngine, simulator: Simulator
) -> tuple[list[float], list[float]]:
    x_list = []
    y_list = []

    for playlog in engine._history.playlogs():
        report = engine.get_report(playlog)
        x_list.append(playlog.clock)
        y_list.append(simulator.calculator.calculate_damage(report))

    return x_list, y_list


def get_cumulative_logs(
    engine: OperationEngine, simulator: Simulator
) -> tuple[list[float], list[float]]:
    x_list: list[float] = []
    y_list: list[float] = []

    cumulated_damage = 0

    for playlog in engine._history.playlogs():
        report = engine.get_report(playlog)
        x_list.append(float(playlog.clock))
        cumulated_damage += simulator.calculator.calculate_damage(report)
        y_list.append(cumulated_damage)

    return x_list, y_list
