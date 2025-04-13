import requests
import yaml
from pathlib import Path
from typing import List, Dict, Any
import time
from simaple.core.jobtype import _kms_job_names, JobType

CLASS_NAMES: list[tuple[str, JobType]] = [
    v for v in list(_kms_job_names.items()) 
    if v[1] != JobType.virtual_maplestory_m
]


def crawl_chuchu_ranking(job_name: str) -> List[Dict[str, Any]]:
    base_url = "https://chuchu.gg/api/getRanking/overall"
    params = {
        "class": job_name,
        "page": 1,
        "world_name": "이노시스"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    characters = []
    
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()

        if "ranking" in data:
            for char in data["ranking"]:
                character = {
                    "name": char["character_name"],
                    "level": char["character_level"],
                    "rank": char["ranking"],
                    "exp": char["character_exp"],
                    "guild": char["character_guildname"],
                    "popularity": char["character_popularity"]
                }
                characters.append(character)
                
        print(f"총 {len(characters)}개의 캐릭터 정보를 추출했습니다.")
        
    except requests.RequestException as e:
        print(f"요청 중 오류 발생: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        
    return characters


def save_characters(characters: List[Dict[str, Any]], file_name: str):
    output_path = Path(f"refs/characters/{file_name}.yaml")
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump({"characters": characters}, f, allow_unicode=True, sort_keys=False, indent=2)
    print(f"캐릭터 정보가 {output_path}에 저장되었습니다.")


def main():
    for job_name, job_type in CLASS_NAMES:
        characters = crawl_chuchu_ranking(job_name)
        if characters:
            save_characters(characters, job_type.value)

if __name__ == "__main__":
    main() 