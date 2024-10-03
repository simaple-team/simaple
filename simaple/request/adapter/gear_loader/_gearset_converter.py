import re

from simaple.core import ExtendedStat, Stat
from simaple.gear.gear_repository import GearRepository
from simaple.request.adapter.gear_loader._converter import get_equipments
from simaple.request.adapter.gear_loader._schema import CharacterItemEquipment


def _line_to_stat(line: str) -> Stat:
    pattern = re.compile(r"([A-Z/가-힣a-z\s]+)\+(\d+)(%?)")
    match = pattern.search(line)
    if not match:
        return Stat()

    option_name = match.group(1).strip()
    option_value = int(match.group(2))
    is_percentage = match.group(3) == "%"

    match (option_name, is_percentage):
        case ("최대 HP", False):
            return Stat(MHP=option_value)
        case ("최대 MP", False):
            return Stat(MMP=option_value)
        case ("최대 HP", True):
            return Stat(MHP_multiplier=option_value)
        case ("최대 MP", True):
            return Stat(MMP_multiplier=option_value)
        case ("공격력", False):
            return Stat(attack_power=option_value)
        case ("마력", False):
            return Stat(magic_attack=option_value)
        case ("올스탯", False):
            return Stat(
                STR=option_value, DEX=option_value, INT=option_value, LUK=option_value
            )
        case ("공격력", True):
            return Stat(attack_power_multiplier=option_value)
        case ("마력", True):
            return Stat(magic_attack_multiplier=option_value)
        case ("올스탯", True):
            return Stat.all_stat_multiplier(option_value)
        case ("몬스터 방어율 무시", True):
            return Stat(ignored_defence=option_value)
        case ("보스 몬스터 공격 시 데미지", True):
            return Stat(boss_damage_multiplier=option_value)
        case ("STR", False):
            return Stat(STR=option_value)
        case ("DEX", False):
            return Stat(DEX=option_value)
        case ("INT", False):
            return Stat(INT=option_value)
        case ("LUK", False):
            return Stat(LUK=option_value)
        case ("공격력/마력", False):
            return Stat(attack_power=option_value, magic_attack=option_value)
        case ("최대 HP/최대 MP", False):
            return Stat(MHP=option_value, MMP=option_value)
        case ("크리티컬 데미지", True):
            return Stat(critical_damage=option_value)
        case _:
            return Stat()


def parse_title_stat(title: str) -> Stat:
    lines = title.split("\n")
    return sum((_line_to_stat(line) for line in lines), Stat())


def _get_title_stat(title_description: str) -> Stat:
    return parse_title_stat(title_description)


def get_equipment_stat(
    item_equipment: CharacterItemEquipment,
    gear_repository: GearRepository,
) -> ExtendedStat:
    total_stat = ExtendedStat()
    item_gears = get_equipments(item_equipment, gear_repository)

    for gear, _ in item_gears:
        total_stat += gear.sum_extended_stat()

    total_stat += ExtendedStat(
        stat=_get_title_stat(
            item_equipment["title"]["title_description"],
        )
    )
    return total_stat
