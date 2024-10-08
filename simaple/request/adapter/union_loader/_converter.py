import re

from simaple.core import ActionStat, ExtendedStat, Stat


def get_stat_from_occupation_description(
    line: str,
) -> ExtendedStat:
    pattern = re.compile(r"([A-Z/가-힣a-z\s]+)([\d\.]+)(%?) 증가")
    match = pattern.search(line)
    if not match:
        raise ValueError(f"Invalid occupation description: {line}")

    option_name = match.group(1).strip()
    option_value_float = float(match.group(2))
    option_value = int(option_value_float)
    is_percentage = match.group(3) == "%"

    match (option_name, is_percentage):
        case ("STR", False):
            return ExtendedStat(stat=Stat(STR_static=option_value))
        case ("DEX", False):
            return ExtendedStat(stat=Stat(DEX_static=option_value))
        case ("INT", False):
            return ExtendedStat(stat=Stat(INT_static=option_value))
        case ("LUK", False):
            return ExtendedStat(stat=Stat(LUK_static=option_value))
        case ("마력", False):
            return ExtendedStat(stat=Stat(magic_attack=option_value))
        case ("공격력", False):
            return ExtendedStat(stat=Stat(attack_power=option_value))
        case ("최대 HP", False):
            return ExtendedStat(stat=Stat(MHP=option_value))
        case ("최대 MP", False):
            return ExtendedStat(stat=Stat(MMP=option_value))
        case ("크리티컬 데미지", True):
            return ExtendedStat(stat=Stat(critical_damage=option_value_float))
        case ("크리티컬 확률", True):
            return ExtendedStat(stat=Stat(critical_rate=option_value))
        case ("방어율 무시", True):
            return ExtendedStat(stat=Stat(ignored_defence=option_value))
        case ("보스 몬스터 공격 시 데미지", True):
            return ExtendedStat(stat=Stat(boss_damage_multiplier=option_value))
        case ("획득 경험치", True):
            return ExtendedStat()
        case ("상태이상 내성", True):
            return ExtendedStat()
        case ("일반 몬스터 공격 시 데미지", True):
            return ExtendedStat()
        case ("버프 지속시간", True):
            return ExtendedStat(action_stat=ActionStat(buff_duration=option_value))

    raise ValueError(f"Unknown option name: {option_name}")
