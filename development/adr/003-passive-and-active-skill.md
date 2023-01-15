# [short title of solved problem and solution]

* Status: proposed
* Deciders: meson3241
* Date: 2022.12.24


## Context and Problem Statement

- 현재는 Passive Skill과 Default Active Skill이 정의되어, 캐릭터의 기준 스펙을 정의할 때 활용되고 있다.
- 그러나, 이들의 정의가 모호하여 직업을 구현하고자 할 때 작성자별로 다른 형태로 구현되고 있다.
- 뿐만 아니라, 실제 최적화 과정에서는 Component를 통해서만 조회 가능한 버프류를 다수 참조해야 한다. 이로 인해 이들의 존재 가치가 불분명하다.
- 이로 인해, 다음을 제안한다.
  - Default Active Skill의 제거
  - Passive Skill의 엄격한 정의 (모든 상시 사용형/onoff 스킬의 Component화)

## Considered Options

### Option 1 (기존 방식)
- Passive Skill을 아래와 같이 정의한다.
  - 사용 불가능한 패시브 스킬

- Default Skill을 아래와 같이 정의한다.
  - 마을에서 100% 가동률을 나타내는 버프형 스킬
  - onoff 스킬
  - 전투 상황에서 100% 가동률을 나타내는 스킬
  - 단, Passive Skill의 정의에 부합하지 않는 스킬

- 위 두 정의에 부합하지 않는 모든 스킬은 Component로 구현되어야 한다.

### Option 2
- Passive Skill을 아래와 같이 정의한다.
  - 사용 불가능한 패시브 스킬

- 위 정의에 부합하지 않는 모든 스킬은 Component로 구현되어야 한다.

### Option 3
- 패시브 스킬을 포함한 모든 스킬은 Component로 구현되어야 한다.


## Pros and Cons of the Options

### [Option 1]

- Good: 전투상태에서 가동률 100%인 모든 버프류 스킬의 정보를 알 수 있으므로, 캐릭터의 중간 정밀도의 스펙 최적화를 위해 Component를 활용한 시뮬레이션 환경을 구성할 필요가 없다.
- Bad: 완전 최적화를 위해서는 어차피 시뮬레이션 환경 구성이 필요하므로, 불필요한 복잡도를 추가하는 시스템이 될 수 있다.
- Bad: 스킬간 분류가 모호하며, onoff스킬이나 버프 스킬 중 전투 상태를 참조하는 경우 분류하기가 애매하다.
- Bad: 상시 가동되는 스킬이더라도, 펫버프로 사용하지 않는 경우 딜레이 참조가 되지 않는다.
- Bad: 시뮬레이션 환경에서 onoff/buff가 가동중임이 확인되지 않아, 시뮬레이션 환경을 사용중인 유저가 혼동을 겪을 수 있다.


### [Option 2]

- Good: 캐릭터의 저정밀도의 스펙 최적화를 위해 Component를 활용한 시뮬레이션 환경을 구성할 필요가 없다.
- Bad: 캐릭터의 버프 상태를 가늠하기 위해 항상 시뮬레이션 환경이 필요하다. 중간 정밀도 이상의 스펙 최적화를 위해 시뮬레이션 환경 구성이 필요하다.
- Good: 스킬간 분류가 명확하다. 100% 정적인 패시브 스킬만이 Passive Skill이 된다.
- Good: 모든 스킬의 딜레이 참조 및 펫버프 딜레이 최적화가 가능하다.
- Good: 모든 스킬의 시뮬레이션 환경에서 onoff/buff 가동 여부를 확인할 수 있다.


### [Option 2]

- Bad: 캐릭터의 스펙 최적화를 위해 언제나 Component를 활용한 시뮬레이션 환경을 구성할 필요가 있다.
- Bad(from Option 2): 캐릭터의 버프 상태를 가늠하기 위해 항상 시뮬레이션 환경이 필요하다.
- Good(from Option 2): 스킬간 분류가 명확하다. 100% 정적인 패시브 스킬만이 Passive Skill이 된다.
- Good(from Option 2): 모든 스킬의 딜레이 참조 및 펫버프 딜레이 최적화가 가능하다.
- Good(from Option 2): 모든 스킬의 시뮬레이션 환경에서 onoff/buff 가동 여부를 확인할 수 있다.
- Good: 모든 정보가 Component로 통합된다.
- Bad: 다수의 버프류 스킬 추가로 인해 시뮬레이션 연산 시간이 길어지고, 시뮬레이션 뷰에 불필요한 패시브 스킬 정보가 노출될 수 있다.


## Decision Proposed

- Option 2

## Decision Outcome

- Option 2
