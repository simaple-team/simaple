skill_info의 response_at_6 필드는 다음과 같이 구성된다.
key: string. 스킬의 이름
value: list{level: int, skill_effect: str}. 레벨에 따른 스킬의 효과

이 때 다음 작업을 수행하는 코드를 작성하라.

1. 두 Text를 비교
2. 공통 텍스트를 추출하고, 값이 다른 부분을 $1, $2와 같은 형식으로 치환
3. level에 따라 달라지는 값을 다음과 같이 구성: skill_name: [{level_1: value_1, level_2: value_2}, ....]
4. 이렇게 얻어진 값을 skill_template.yaml에 정리