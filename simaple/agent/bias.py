from loguru import logger

def generate_logit_bias(
    all_skill_names: list[str],
    buff_skill_names: list[str],
    damage_skill_names: list[str],

    buff_skill_bonus: float = 5.0,
    damage_skill_bonus: float = 2.0,
    buff_priority_bonus: float = 2.0,
    damage_priority_bonus: float = 2.0,
) -> list[float]:
    """
    스킬 우선순위에 따라 로짓 편향 생성
    """
    bias = [0.0] * len(all_skill_names)

    unselected_skills = set(all_skill_names) - set(buff_skill_names) - set(damage_skill_names)

    for skill_name in unselected_skills:
        logger.warning(f"선택되지 않은 스킬: {skill_name}")

    for idx, skill_name in enumerate(buff_skill_names):
        buff_skill_index = all_skill_names.index(skill_name)
        bias[buff_skill_index] += buff_skill_bonus
        bias[buff_skill_index] += buff_priority_bonus * (len(buff_skill_names) - idx) / len(all_skill_names)

    for idx, skill_name in enumerate(damage_skill_names):
        damage_skill_index = all_skill_names.index(skill_name)
        bias[damage_skill_index] += damage_skill_bonus
        bias[damage_skill_index] += damage_priority_bonus * (len(damage_skill_names) - idx) / len(all_skill_names)

    return bias
