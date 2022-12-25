# [short title of solved problem and solution]

* Status: resolved
* Deciders: meson3241, icepeng
* Date: 2022.12.24


## Context and Problem Statement

DOT 피해는 다른 피해와 다르게, 아래와 같은 특징을 가진다.
- 피해 계산 로직이 다른 로직과 다르다.
- 실제 인게임에서는, DOT 구현이 1초 주기로 몬스터에게 피해가 가는 형태로 구현된다. (모든 피해가 동시에 발생)
- 현재는 이를 틱데미지 형태로 구현하고 있는데, 이는 피해 계산과 피해 방식에서 실제와 차이가 있으므로 이를 해결할 필요가 있다.

## Considered Options

* 공통 사항
  - 도트데미지는 별도의 태그를 가지는, 비-DEALT event 로 간주된다.

* Option1
  - MobComponent와 MobState를 정의하고, 해당 MobState에 DOT 영역을 제공한다.
  - Mobstate의 DOT 영역을 bind를 통해, 도트 피해를 주는 스킬이 변경을 가한다.
  - 도트 데미지는 MobComponent.elapse에 구현된다. 
* Option2
  - MobComponent와 MobState를 정의하고, 해당 MobState에 DOT 영역을 제공한다.
  - 각 Component는 DOT Tagged event를 발생시킬 수 있다.
  - MobComponent는 listening_action 을 통해, *.DOT 이벤트를 listen하고 이를 바탕으로 자신의 상태를 업데이트한다.
  - 도트 데미지는 MobComponent.elapse에 구현된다.
* Option3
- Component가 자체적으로 DOTState를 가지고, elapse 과정에서 각자 DOT 피해를 발생시킨다.

## Decision Outcome

- Choose Option 2

## Pros and Cons of the Options <!-- optional -->

### [Option 1]

- Good: Mobstate를 명시하여, 실제 게임에서와 같이 모든 도트 데미지를 동시에 발생시킬 수 있다.
- Good: 추후 다양한 MobState를 추가할 때 보다 다양한 상황을 쉽게 묘사할 수 있다.
- Bad: bind가 사용되어 Mob 객체가 자신의 상태를 명시적으로 핸들링할 수 없다.

### [Option 2]

- Good: Mobstate를 명시하여, 실제 게임에서와 같이 모든 도트 데미지를 동시에 발생시킬 수 있다.
- Good: 추후 다양한 MobState를 추가할 때 보다 다양한 상황을 쉽게 묘사할 수 있다.
- Good: listening_action을 bind 대신 사용하므로 서로의 컨텍스트가 온전히 분리된다.
- Bad: 도트데미지의 관리 로직이 스킬의 Component에 존재하지 않으므로 도트 피해의 테스트가 어렵고, 도트 피해의 발생이 Component의 관점에서 불투명하다.

### [Option 3]
- Bad: 실제 게임에서와 같이 모든 도트 데미지를 동시에 발생시킬 수 없고, 제각각 도트 데미지를 계산한다.
- Bad: 전체 도트 피해 상태를 확인하기 어려우므로 도트 퍼니셔의 관리가 어렵다.
- Bad: 추후 MobState를 추가한다면 이 방식은 직관적이지 못하고, 동일한 역할을 두 가지의 다른 방법으로 처리하게 된다.
- Good: Component가 도트 데미지 피해 계산을 온전히 담당하므로 DOT 계산 방식이 직관적이다.
