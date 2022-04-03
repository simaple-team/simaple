import os

_ABS_PATH = os.path.join(os.path.dirname(__file__), "resources")


def parse_resource_path(pathlike: str, default_file_format="yaml"):
    target_path = os.path.join(_ABS_PATH, pathlike)

    if os.path.exists(target_path):
        return target_path

    target_path = target_path + ".yaml"

    if not os.path.exists(target_path):
        raise FileNotFoundError(f"Queried resource {pathlike} not exists")

    return target_path
