from simaple.app.domain.simulator import Simulator
from simaple.simulate.engine import OperationEngine


def get_damage_logs(
    engine: OperationEngine, simulator: Simulator
) -> tuple[list[float], list[float]]:
    x_list = []
    y_list = []

    for playlog in engine._history.playlogs():
        x_list.append(playlog.clock)
        entry = engine.get_simulation_entry(playlog)
        y_list.append(simulator.calculator.calculate_damage(entry))

    return x_list, y_list


def get_cumulative_logs(
    engine: OperationEngine, simulator: Simulator
) -> tuple[list[float], list[float]]:
    x_list: list[float] = []
    y_list: list[float] = []

    cumulated_damage = 0.0

    for playlog in engine._history.playlogs():
        x_list.append(float(playlog.clock))
        entry = engine.get_simulation_entry(playlog)
        cumulated_damage += simulator.calculator.calculate_damage(entry)
        y_list.append(cumulated_damage)

    return x_list, y_list
