"""
this tool converts potential map into simaple potential db.
This may generate DB in simaple/gear/blueprint/db.yaml
"""

import json
import yaml

from simaple.gear.blueprint.potential_blueprint import PotentialType
from simaple.gear.potential import PotentialTier


with open("item-option.json") as f:
    raw = json.load(f)

from typing import Optional


def get_tier(key_string: str) -> PotentialTier:
    tier_value = int(key_string) // 10000

    if tier_value == 0:
        return PotentialTier.normal
    elif tier_value == 1:
        return PotentialTier.rare
    elif tier_value == 2:
        return PotentialTier.epic
    elif tier_value == 3:
        return PotentialTier.unique
    elif tier_value == 4:
        return PotentialTier.legendary

    return None


def get_type(key_string: str) -> PotentialType:
    type_value = (int(key_string) % 10000) // 1000
    if type_value == 0:
        return PotentialType.normal
    elif type_value == 2:
        return PotentialType.additional

    raise ValueError



naming_map = {
    'STR : +#incSTR': "STR",
    'LUK : +#incLUK': "LUK",
    'INT : +#incINT': "INT",
    'DEX : +#incDEX': "DEX",
    "최대 HP : +#incMHP": "MHP",
    "최대 HP : +#incMMP": "MMP",
    "데미지 : +#incDAMr%": "damage_multiplier",
    "올스탯 : +#incSTR": "all_stat",
    "STR : +#incSTRr%": "STR_multiplier",
    "LUK : +#incLUKr%": "LUK_multiplier",
    "INT : +#incINTr%": "INT_multiplier",
    "DEX : +#incDEXr%": "DEX_multiplier",
    "몬스터 방어율 무시 : +#ignoreTargetDEF%": "ignored_defence",
    "보스 몬스터 공격 시 데미지 : +#incDAMr%": "boss_damage_multiplier",
    "마력 : +#incMADr%": "magic_attack_multiplier",
    "공격력 : +#incPADr%": "attack_power_multiplier",
    "최대 MP : +#incMMP": "MMP_multiplier",
    "크리티컬 확률 : +#incCr%": "critical_rate",
    "올스탯 : +#incSTRr%": "all_stat_multiplier",
    "최대 MP : +#incMMPr%": "MMP_multiplier",
    "공격력 : +#incPAD": "attack_power",
    "마력 : +#incMAD": "magic_attack",
    "최대 HP : +#incMHPr%": "MHP_multiplier",
    "크리티컬 데미지 : +#incCriticaldamage%": "critical_damage",
}

# "42041":{"optionType":11, 방어구/장신구
# "42063":{"optionType":10, 무기


translation_map = {
    "incINTr": "INT_multiplier",
    "incSTRr": "STR_multiplier",
    "incDEXr": "DEX_multiplier",
    "incLUKr": "LUK_multiplier",
    "incSTR": "STR",
    "incLUK": "LUK",
    "incDEX": "DEX",
    "incINT": "INT",
    "incMHP": "MHP",
    "incMMP": "MMP",
    "incRewardProp": None, # 아이템 드랍률
    "incCr": "critical_rate",
    "incPDDr": None, # 방어력%
    "incPDD": None, # 방어력
    "incCriticaldamage": "critical_damage",
    "incDAMr": "damage_multiplier",
    "RecoveryHP": None, # 4초당 HP 회복
    "RecoveryMP": None, # 4초당 Mp 회복
    "incTerR": None, # 속성 내성
    "boss": "boss_damage_multiplier", # special indicator; boss 필드가 있으면 damage_multiplier를 바꿈
    "mpconReduce": None,  # 모든 스킬의 MP 소모 -
    "incSpeed": None, # 이동 속도
    "incPAD": "attack_power",
    "incMAD": "magic_power",
    "ignoreTargetDEF": "ignored_defence",
    "incEXPr": None, # 경험치 획득 %
    "DAMreflect": None, #'#prop% 확률로 받은 피해의 #DAMreflect%를 반사'
    "RecoveryUP": None, #HP 회복 아이템 및 회복 스킬 효율 : +#RecoveryUP
    "time": None, #'피격 후 무적시간 : +#time초'
    "face": None, # 표정
    "incMMPr": "MMP_multiplier",
    "incMHPr": "MHP_multiplier",
    "ignoreDAM": None, #'피격 시 #prop% 확률로 데미지 무시'
    "ignoreDAMr": None, #'피격 시 #prop% 확률로 데미지의 #ignoreDAMr% 무시'
    "reduceCooltime": None, #'모든 스킬의 재사용 대기시간 : -#reduceCooltime초
    "MP": None, #'공격 시 #prop% 확률로 #MP의 MP 회복'
    "HP": None, #'공격 시 #prop% 확률로 #HP의 HP 회복'
    "incDEXlv": None, #'10레벨당 DEX'
    "incINTlv": None, #'10레벨당 INT'
    "incSTRlv": None, #'10레벨당 STR'
    "incLUKlv": None, #'10레벨당 LUK'
    "incMADlv": None, # 10레벨당 마력
    "incPADlv": None, # 10레벨당 마력
    "prop": None, # 공격 시 #prop% 확률로 #MP의 MP 회복
    "incMADr": "magic_attack_multiplier",
    "incJump": None, # 점프력
    "level": None, # 쓸스킬
    "incMesoProp": None, # 메획
    "incAllskill": None, # 모든 스킬 레벨
    "incAsrR": None, # 상태이상 내성
    "incPADr": "attack_power_multiplier",
    "attackType": None, # 공격시 효과 적용
}

def translate_key_as_simaple_entity(k: str) -> Optional[str]:
    return translation_map.get(k, k)


def translate_description(description) -> dict[str, int]:
    output = {}
    for desc_key, desc_value in description.items():
        translated_key = translate_key_as_simaple_entity(desc_key)
        if translated_key is None:
            return None
        
        output[translated_key] = desc_value

    if "boss_damage_multiplier" in output:
        output["boss_damage_multiplier"] = output.pop("damage_multiplier")

    return output


db = {}

name_map = set()

for k, v in raw.items():
    tier = get_tier(k)
    if tier is None:
        continue

    field_description = naming_map.get(v["string"], v["string"])
    effects = {}
    breaks = False
    for level_key, level_description in v["level"].items():
        description = translate_description(level_description)
        if description is None:
            breaks = True
            break

        effects[int(level_key)] = description

    if breaks:
        continue

    if len(effects) != 25:
        raise ValueError

    listed_effects = [effects[idx] for idx in range(1, 26)]

    if tier.value not in db:
        db[tier.value] = []

    potential_type = get_type(k).value
    weapon_flag = (v.get("optionType") == 10)

    db[tier.value].append({
        "name": field_description,
        "effect": listed_effects,
        "key": int(k),
        "desc": v["string"],
        "type": potential_type + (f"_weapon" if weapon_flag else ""),
    })

## Rearrange db table into query-value map
    # dict[type][tier][level]
rearranged_db = {}

for tier, rows in db.items():
    for row in rows:
        for idx, effect in enumerate(row["effect"]):
            type_map = rearranged_db.setdefault(row["type"], {})
            tier_map = type_map.setdefault(tier, [{} for _ in range(25)])
            effect_map = tier_map[idx]
            effect_map[row["name"]] = effect


with open("db.yaml", "w") as f:
    yaml.safe_dump(rearranged_db, f, allow_unicode=True)

#with open("dump.yaml", "w") as f:
#    yaml.safe_dump(db, f, allow_unicode=True)
