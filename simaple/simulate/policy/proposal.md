

- purpose: exact pipelining.
  - descriptive & deterministic.
  - Autofill이 필수적.
    - Why?
    - We need `Baseline`
    - Baseline을 알고 있으면 편리할 수 있다.
    - Comparison이 가능하면 더 좋다.
  - 

- Existing Baseline을 도시해본다.
- Text history Area가 필요하다. (with timestamp, maybe?)
  - why?
    - 내가 지금까지 수행한 행동 이력을 확인하기가 어렵다.
    - 내가 뭔가 잘못 수행했더라도, 그 사실을 확인하기가 어렵다.
    - 비-개발자라면 몰라도, 개발자는 텍스트로 보는것이 더 편리하다.
  - 얻을 수 있는 이점
    - 작업 히스토리를 명확히 확인할 수 있다.
    - 
  - 기능
    - 현재까지 입력한 내용을 보여준다.
      - 내용이라 함은, 다음을 이야기한다: 아이콘, timestamp, action(type, value)
    - 옆에 아이콘이 나오면 더 좋을 것 같다.
    - CLI 형태의 입력기도 추가되면 더 유용하다.
    - Edit 기능이 필요한가?
      -> 아직은 필요하지 않다. Only display.
  - 다른 대안은 없는가?
    - Web browser상에서 Text를 노출하지 않고, Editor로만 접근하는 정책을 생각해 볼 수 있다.
    - 
  - misc
    - Action Type으로 ElapseAndDuration이 추가되어야 한다. (하나의 Atomic operation으로 정의되는 것이 맞다)



### Inroduce OpCode

- OpCode는 Human이 Action을 직접 기입할 때 발생하는 오류를 방지하고, 가독성을 증진시켜 쉽게 행동을 제어하기 위한 layer입니다.
- OpCode는 Action의 제어를 돕고, Action의 low-level interface를 한 단계 감싸 적절한 형식으로 값을 기입하는데 그 목적을 두고 있습니다.
- OpCode는 다음을 지원해서는 안됩니다. 아래 기능은 OpCode를 생성하는 Human 또는 Policy의 책임입니다. 이러한 기능은 python code로서 기술되는 것이 권장됩니다.
  - for과 같은 반복문
  - if와 같은 분기
  - 전체 상태(environment)에 대한 참조
- OpCode는 다음을 지원해야 합니다.
  - 모호한 Action Payload의 method별 명세에 대한 적절한 wrapping
  - OpCode 내 수행에 의한 직전 Event에 대한 참조
  - line 단위 string ser/deserialize 인터페이스

