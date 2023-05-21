# Component code writting rule

### Component id
- 모든 Component는 반드시 id를 포함해야 합니다.
- id는 다음과 같은 포맷으로 주어지는 string입니다.
  - {wz-id}-{component-index}
- wz-id 는 해당 스킬에 대응되는 skill.wz 내 스킬의 id 입니다.
  - 해당 wz-id로 wz 내에서 조회하면, 대응되는 스킬이 조회되어야 합니다.
  - 여러 component들은 같은 wz-id를 가질 수 있습니다.
  - Wz file 내에 존재하지 않는 스킬은 이 값으로 0을 가져야 합니다.
- component-index는, 동일한 wz-id를 가지는 Component간의 구분을 위한 추가 인덱스입니다.
  - 0이 아닌 wz-id에 대해, 
    - component-index는 특정 wz-id에 대해, 0부터 시작하여, 연속적으로 사용되어야 합니다. 예를 들어, 1-1 없이 1-0과 1-2가 제시되어서는 안됩니다.
    - (wz-id, component-index)는 중복되어서는 안됩니다.
  - wz-id가 0일 때,
    - component-index는 [RFC1123](https://datatracker.ietf.org/doc/html/rfc1123) 을 준수하는 임의의 값이 올 수 있습니다.
      - 길이가 63자를 넘지 않아야 합니다.
      - 알파벳 소문자, 숫자, '-'만을 포함해야 합니다.
      - 첫 글자와 마지막 글자가 알파벳 소문자 또는 숫자여야 합니다.

- 기타 테스트 목적 또는 아직 확정되지 않은 값을 명시하기 위해, 알파벳을 포함하여 wz-id를 작성할 수 있습니다. 이는 해당 id가 실재하지 않으며, wz file내에서 조회될 수 없음을 의미합니다.
- 내부적으로, id format을 강제하는 코드는 제공하지 않습니다.
