import os

from simaple.data.jobs.builtin import get_kms_jobs_repository


# read all icon files in directory, and remove if there is no corresponding component.
# log component id if there is no corresponding icon file.
def check_icon():
    components = get_kms_jobs_repository().get_all(kind="Component")
    ids = [str(component.data.get("id")).split("-")[0] for component in components]
    icon_files = os.listdir("webui/public/icons")

    for icon_file in icon_files:
        if icon_file.split(".")[0] not in ids:
            print("removing ", icon_file)
            os.remove(f"webui/public/icons/{icon_file}")

    for id in ids:
        if f"{id}.png" not in icon_files:
            print("no icon for ", id)

check_icon()