import os
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from simaple.core.jobtype import JobType

from simaple.request.external.nexon.api.character.skill import (
    get_every_skill_levels,
    AggregatedCharacterSkillResponse,
)
from simaple.request.external.nexon.api.character.common import CharacterIDWithDate, get_character_ocid
from typing import TypedDict



class IndividualCharacter(TypedDict):
    job_type: JobType
    name: str
    level: int
    rank: int
    exp: int
    guild: str
    popularity: int


def load_characters(job_type: JobType) -> list[IndividualCharacter]:
    with open(f"refs/characters/{job_type.value}.yaml", "r") as f:
        return yaml.safe_load(f)["characters"]


def clean_skill_info(skill_info: AggregatedCharacterSkillResponse) -> dict[str, dict[str, list[dict[str, Any]]]]:
    result: dict[str, dict[str, list[dict[str, Any]]]] = {}
    
    # 각 response_at에 대해 처리
    for grade, response in skill_info.items():
        if grade not in ["response_at_5", "response_at_6", "response_at_hyper_passive", "response_at_hyper_active"]:
            continue
            
        # 스킬별로 정보를 그룹화
        skill_groups: dict[str, list[dict[str, Any]]] = {}
        for skill in response["character_skill"]:
            skill_name = skill["skill_name"]
            if skill_name not in skill_groups:
                skill_groups[skill_name] = []
            
            skill_groups[skill_name].append({
                "level": skill["skill_level"],
                "skill_effect": skill["skill_effect"]
            })
        
        result[grade] = skill_groups
    
    return result


def get_skill_info(character: IndividualCharacter) -> dict[str, Any]:
    host = "https://open.api.nexon.com"
    access_token = os.environ["NEXON_API_KEY"]
    date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    ocid = get_character_ocid(host, access_token, character["name"])
    
    # 스킬 정보 가져오기
    skill_payload = CharacterIDWithDate(ocid=ocid, date=date)
    skill_info = get_every_skill_levels(host, access_token, skill_payload)
    
    return {
        "skill_info": clean_skill_info(skill_info),
    }

from tqdm import tqdm

def main():
    job_type = JobType.archmagetc
    characters = load_characters(job_type)
    merged_skills = {}
    
    # 모든 ocid의 스킬 정보를 수집
    for character in tqdm(characters[:30:2]):
        skill_info = get_skill_info(character)["skill_info"]

        # 각 response_at에 대해 처리
        for response_at, skills in skill_info.items():
            if response_at not in merged_skills:
                merged_skills[response_at] = {}
            
            # 각 스킬에 대해 처리
            for skill_name, skill_list in skills.items():
                if skill_name not in merged_skills[response_at]:
                    merged_skills[response_at][skill_name] = []
                
                # 새로운 스킬 정보 추가
                merged_skills[response_at][skill_name].extend(skill_list)
    
    # 결과를 파일로 저장
    output_path = Path("refs/skill_info.yaml")
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump({"skill_info": merged_skills}, f, allow_unicode=True, sort_keys=False, indent=2)


if __name__ == "__main__":
    main()
