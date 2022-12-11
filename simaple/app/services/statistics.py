from simaple.app.services.base import PlayLog


def get_damage_logs(logs: list[PlayLog]):
    x_list = []
    y_list = []

    for resp in logs:
        x_list.append(resp.clock)
        y_list.append(resp.damage)

    return x_list, y_list


def get_cumulative_logs(logs: list[PlayLog]):
    x_list = []
    y_list = []

    cumulated_damage = 0

    for resp in logs:
        x_list.append(resp.clock)
        cumulated_damage += resp.damage
        y_list.append(cumulated_damage)

    return x_list, y_list
