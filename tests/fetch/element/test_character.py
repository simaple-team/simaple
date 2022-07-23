from simaple.fetch.element import CharacterElement


def test_item_element():
    element = CharacterElement()

    with open("tests/fetch/resources/character.html", encoding="euc-kr") as f:
        html_text = f.read()

    result = element.run(html_text)
    assert result == {
        "name": "생분자",
        "level": 275,
        "world": "크로아",
        "job": "마법사/아크메이지(불,독)",
        "pop": "1,860",
        "guild": "Shiny",
        "meso": "169,913,574",
        "point": "2,735",
        "damage_factor": "104,185,958 ~ 108,527,036",
        "MHP": "43,438",
        "MP": "106,562",
        "STR": "5044",
        "DEX": "4,535",
        "INT": "52,802",
        "LUK": "8,138",
        "critical_damage": "75%",
        "boss_damage_multiplier": "303%",
        "ignored_defence": "96%",
        "immunity": "45",
        "stance": "100%",
        "armor": "21769",
        "speed": "140%",
        "jump": "123%",
        "starforce": "345",
        "honor_point": "646,603",
        "arcaneforce": "1360",
        "ability": [
            "버프 스킬의 지속 시간 50% 증가",
            "상태 이상에 걸린 대상 공격 시 데미지 7% 증가",
            "크리티컬 확률 20% 증가",
        ],
        "hyperstat": [
            "공격력과 마력 18 증가",
            "지력 150 증가",
            "운 60 증가",
            "크리티컬 확률 13% 증가",
            "크리티컬 데미지 12% 증가",
            "방어율 무시 36% 증가",
            "데미지 36% 증가",
            "보스 몬스터 공격 시 데미지 43% 증가",
        ],
        "trait": {"카리스마": 100, "통찰력": 100, "의지": 100, "손재주": 100, "감성": 100, "매력": 100},
    }
