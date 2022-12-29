# Component 유닛 테스트

* Status: accepted
* Deciders: meson3241, icepeng
* Date: 2022-12-29


## Context and Problem Statement

현재 컴포넌트 유닛 테스트는 다음과 같은 과정을 거친다.
* Store fixture를 생성한다.
* component를 StoreEmbeddedObject로 컴파일한 fixture를 테스트 대상으로 삼는다.
  * reducer, view method의 state 인자를 partial apply한다.
  * State의 Entity들을 멤버로 추가한다. ex) `component.lasting.enabled()`

이때, State 내의 Entity 이름이 reducer, view의 이름과 겹치면 덮어써지며 예상하기 어려운 오류가 발생한다. 더불어, 순수 함수를 테스트하는데 있어 Store 의존성이 따라오고, 어노테이션 지원이 없는 것이 불편하다.

## Considered Options

* Store 의존성을 제거하고, state chaining으로 테스트한다.
* Store 의존성을 유지하고, StoreEmbeddedObject 구현을 변경한다.

## Decision Outcome

Chosen Option: Store 의존성을 제거하고, state chaining으로 테스트한다.

## Pros and Cons of the Options <!-- optional -->

### Store 의존성을 제거하고, state chaining으로 테스트한다.

```py
def test_use_keydown_component_many_time(
    keydown_fixture: tuple[KeydownComponent, KeydownState, float]
):
    # given
    keydown_component, keydown_state, keydown_delay = keydown_fixture

    # when
    for _ in range(6):
        keydown_state, _ = keydown_component.use(None, keydown_state)
        keydown_state, _ = keydown_component.elapse(keydown_delay, keydown_state)

    # then
    assert keydown_state.is_running()
```

* Good: 테스트에서 어노테이션 지원을 받을 수 있다. 리듀서, 뷰 등의 이름이 변경될 시 IDE의 rename 지원을 받을 수 있다.
* Good: 테스트의 결합도가 낮아진다.
* Bad: 테스트 코드에 `state, event = component.method(payload, state)` 형태의 반복이 많이 발생한다.

### Store 의존성을 유지하고, StoreEmbeddedObject 구현을 변경한다.

```py
def test_use_keydown_component_many_time(keydown_fixture):
    # given
    keydown_component, keydown_delay = keydown_fixture

    # when
    for _ in range(6):
        keydown_component.use(None)
        keydown_component.elapse(keydown_delay)
    
    # then
    assert keydown_component.state.keydown.is_running()
```

* Good: 테스트 코드가 간결하다.
* Bad: assert 대상이 되는 state의 타입 정보가 없어 테스트를 작성할 때 파일을 열어보는 맥락 전환이 자주 발생한다.
