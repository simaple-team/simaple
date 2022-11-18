## simaple.simulate

simulate 모듈은 인게임 내에서 사용되는 스킬을 통한 작용을 묘사합니다.
simulate 모듈은 maplestory_dpm_calc와 가장 대조적인 모듈입니다.


## 이념
simulate 모듈은 Redux Pattern을 사용하여 전체 시스템을 묘사하고 시뮬레이션을 동작시킵니다.

모든 상태는 Store에 저장됩니다. 
상태는 dispatcher에 의해서 변경될 수 있습니다.
simaple은 스킬을, State를 변경시키는 메서드의 집합으로 간주합니다. 이를 표현하기위해 Component class를 제공합니다.
Component는 동일한 값을 참조하는 dispatcher의 집합입니다. 이것은 게임 내에서의 스킬 객체 하나에 대응될 수 있습니다.

모든 연산 흐름은 상태를 기준으로 설계됩니다. 
예시로, A 스킬이 B 스킬의 쿨타임을 변경하는 경우를 생각해 봅시다. 이 때 행위의 주체는 A 스킬의 트리거이지만, 실제로 변경되는 것은 B스킬의 상태입니다. 따라서 이 트리거는 B 스킬의 상태 기술에 작성되게 됩니다.
이것은 얼핏 느끼기에 부당하게 여겨집니다; 액션의 사용이 완결된 이후 그 결과가 다른 스킬에 영향을 미치는 것이 자연스럽습니다. 그러나 이것은 단일 액션이 여러 차례의 연쇄를 거쳐 상태를 변경하는 동작을 야기합니다. 우리는 다음 원칙을 고수합니다.

`하나의 액션으로 야기되는 상태 변화는 한 번에 일어난다`

하나의 액션이 여러 차례의 상태 변화를 야기하는 논리 흐름은 시스템을 제어하는 `Player` 입장에서 시스템에 대한 이해를 어렵게 합니다. `Player`는 스스로의 동작이 어떤 부수-효과를 일으킬지 예측하지 못하게 됩니다. 모든 in-system action dispatching은 단일 액션 처리에 국한되어야 하며 Event의 Action으로의 재해석은 반드시 `Player` 에 의해서 통제되어야 합니다.


## Description

simaple은 redux 구조를 참조한 시뮬레이션 시스템을 차용하고 있습니다. 이를 참고해서 문서를 읽으면 보다 손쉬운 아키텍처 이해가 가능합니다.

- Action
  모든 사용자의 행동은 Action에 대응됩니다. 시뮬레이션은 사용자가 하나의 Action을 생성하여 제공하는것으로부터 시작됩니다.
  Action은 게임 내에서 캐릭터에게 내리는 명령에 대응됩니다. 특정 스킬을 누르거나, 특정 시간동안 행동 없이 대기하는 것이 Action이 됩니다.
  Action은 name, method, payload의 속성을 가집니다. 이들에 대한 설명은 reducer에서 언급됩니다.

- Event
  Event는 Action으로 인한 결과입니다. Event는 Action으로 인해 발생한 delay, damage와 같은 처리가 필요한 것과 특정 스킬의 실행 사실을 안내하는 로깅 목적의 Event로 크게 나눌 수 있습니다. Event는 반드시 처리될 필요는 없습니다; delay event를 참조하여 전체 시스템의 시간을 경과시키는 것 이외에 그 어떤 이벤트도 필수적으로 처리될 필요는 없어야 합니다.
  경과시간 이벤트는 이벤트 중에서 유일하게 처리를 요구하는 Event입니다. 이는 Player가 스킬 캔슬 등을 통해 명시된 delay 이하의 시간많은 적용할 수 있도록 하기 위함입니다.

- State
  State는 묘사하고자 하는 캐릭터의 스킬들이 가지고 있는 상태를 의미합니다. 일반적으로, Action은 State를 변경시킨 후 Event를 발생시킵니다. State들을 통해 Action에 의해 변경되어야 하는 모든 정보를 담고 있어야 합니다. 반대로, 어떠한 상태도 State 이외의 방법을 통해 모델링 되어 Action에 의해 변경되면 안됩니다.

- Store
  Store는 시스템 내의 `모든` State가 저장된 공간입니다. Single-source-of-truth 에 입각하여, 모든 상태는 Store에 저장되어 있어야 합니다. 

- Dispatcher
  Dispatcher는 상태를 변화시키는 방법에 대한 기술입니다. 위에서 안내된 정의 덕분에, 모든 상태를 변화시키는 행동은 아래와 같은 인터페이스를 가질 것입니다. 이를 Dispatcher라고 부릅니다.
  `(Store, Action) -> (Event)`
  Dispatcher의 정의는 아름답지는 않습니다; Dispatcher는 분명히 상태를 변화시키지만, 그것은 인자로 받은 Store를 변경함을 의미합니다. 뿐만 아니라, Dispatcher는 Store 내 State의 immutability를 보장하지도 않습니다.

- Reducer
  Dispatcher는 비-일급 함수라는 nature때문에, 개발자에게 노출되는 인터페이스로는 적절하지 않습니다. 따라서, simaple은 Reducer라는 일급 함수 인터페이스를 제공하여 개발자로 하여 직관적이고 sustainable한 코드를 작성하도록 지원합니다.
  Reducer는 아래와 같은 type을 가지는 함수입니다.
  `(Any, ...State) -> (tuple(...State), optional[list[event]]`
  Reducer는 일급 함수입니다; Reducer는 인자로 받는 State들과 반환하는 State tuple의 길이와 type이 일치해야 합니다. Reducer는 내부적으로 `ReducerMethodWrappingDispatcher` 를 통해 Dispatcher로 감싸지는데, 이를 위해 State의 type이 일치해야 합니다.
  Reducer는 또한 get_state(store: Store)와 set_state(store: Store) 메서드를 지원하여 dispatcher로 하여금 적절한 state를 바인딩하도록 지원해야 합니다.

  Reducer는 일급 함수이지만, 그 구성이 복잡합니다. 이러한 복잡함은 simaple이 다중 상태변화 시스템을 지원하기 위함입니다. 하지만 개발자 입장에서 위의 규칙을 전부 준수하면서 Reducer를 추가하는 것은 매우 불편하고 어렵습니다. 따라서 개발자는 Component를 통해 손쉽게 Reducer를 구현하고 이를 Dispatcher로 감싸게 됩니다.

- Component
  Component는 simaple simulation의 핵심입니다. Component가 가지는 인스턴스 메서드들은 @reducer_method 로 decorate됨으로서 reducer로 손쉽게 변환됩니다.

  간단한 예시를 살펴봅니다.

  ```python
  class AttackSkillComponent(Component):
      name: str
      damage: float
      hit: float
      cooldown: float = 0.0
      delay: float

      def get_default_state(self):
          return {
              "cooldown_state": CooldownState(time_left=0),
          }

      @reducer_method
      def elapse(self, time: float, cooldown_state: CooldownState):
          cooldown_state = cooldown_state.copy()
          cooldown_state.elapse(time)
          return cooldown_state, self.event_provider.elapsed(time)

      @reducer_method
      def use(self, _: None, cooldown_state: CooldownState):
          cooldown_state = cooldown_state.copy()

          if not cooldown_state.available:
              return cooldown_state, self.event_provider.rejected()

          cooldown_state.set_time_left(self.cooldown)

          return cooldown_state, [
              self.event_provider.dealt(self.damage, self.hit),
              self.event_provider.delayed(self.delay),
          ]
  ```
  Component는 크게 세 부분으로 이루어집니다.
  첫번째 부분은 Component의 생성자를 정의하는 부분입니다. Component 는 `pydantic.BaseModel`을 상속받기 때문에 `pydantic.BaseModel`의 생성자 정의 방식을 활용하여 컴포넌트가 정의되기 위해 필요한 정보를 명시합니다.
  자세한 용법은 `pydantic.BaseModel`의 문서를 참조합니다.

  두번째로, `get_default_state` 를 정의합니다. 모든 `Component`는 해당 메서드를 정의해야 하는데, 이는 Component에 정의된 Reducer들이 인자로 받아가는 `State`가 존재하지 않을 때 초기값을 지정하여 전달해주기 위함입니다.

  세번째로, `@reducer_method`로 장식된 메서드들이 정의됩니다. 이 함수의 `signature`에 주목하십시오. 
  `elapse` 메서드는 두번째 인자로 `cooldown_state`를 받고 있습니다. 이 변수명은 임의로 선택된 값이 아닙니다. 이는, 우리가 `get_default_state`에서 `cooldown_state`에 대한 초기값을 지정해 준 것에 대응됩니다. 즉, 이 메서드는 해당 값이 존재하지 않으면 `get_default_state()["cooldown_state"]` 의 값을 전달받습니다. 함수의 첫 인자의 변수명은 호출한 Action의 payload값이 수신되기에 자유로운 변수명을 선택하여도 괜찮습니다.
  마지막으로, 반환값에 주목합니다. 반환값의 첫 인자는 받아온 state 또는 `tuple[...State]`여야만 합니다. 이를 통해 값이 다시 store에 전달되고 업데이트됩니다.

  Component는 여러 state를 지정할 수 있으며, 다양한 reducer를 가질 수 있습니다. 메서드를 reducer로 취급하기 위해서는 `@reducer_method` decorator를 적용하기만 하면 됩니다. 이들 reducer들은 `export_dispatcher` 메서드를 통해 dispatcher로 wrapping 됩니다. dispatcher 는 `{component.name}`와 `{method name}`이 action의 name과 method에 해당하는 경우, 해당 action을 정의된 reducer를 통해 처리되도록 합니다. 예를 들어, 컴포넌트`Component(name="A", ...)`의 `use` 메서드는 `Action(name="A", mtehod="use")`에 의해 호출될것입니다.

  특수하게, `name="*"`로 지정된 Action 또한 컴포넌트에서 수신하여 대응되는 method를 트리거합니다.

  이같은 기술 방식은, 하나의 Component가, 특정 State들에 연관된 Action을 한데 모아서 잘 정의되도록 합니다. 이는 게임에서 하나의 **스킬** 에 해당합니다; 즉, 우리는 `Component`를 통해 스킬 객체를 가독성있게, 유지보수 가능하게 관리할 수 있습니다.

- Component간의 연계
  때때로, 스킬은 다른 스킬과 상호작용합니다. 이들은 다른 스킬이 발동되었을 때 자신의 이벤트를 발생시키거나, 상태를 변경해야 합니다. 
  simaple 에서, 이러한 연계는 두 가지 방법으로 지원됩니다. `앱솔루트 킬` 스킬로 인해 `빛과 어둠의 세례`스택이 증가하는 상황을 상정해 봅시다.
  - 모든 `Component` 는 `listening_actions` 필드를 가지고 있습니다. `Component`를 생성할 때 `listening_actions` 필드에 `{$target_action_signature: $target_method}` 형태의 dictionary 값을 전달하면, `Component.export_dispatcher`를 통한 Dispatcher building 시점에서 해당 이벤트를 추가로 listen합니다. 이 경우, 아래와 같이 컴포넌트를 생성하게 될 것입니다. 스킬을 사용하는 것은 보편적으로 `use` 메서드에 대응된다는 점을 상기하십시오. `빛과 어둠의 세례` 스킬의 스택 수를 하나 증가시키는 메서드가 `increase_stack` 으로 정의되었다고 가정합니다.
    ```python
    component = AttackSkillComponent(
      name="빛과 어둠의 세례",
      listening_actions={
        "앱솔루트 킬.use": "increase_stack"
      }
    )
    ```
  - 관점을 다르게 볼 수도 있습니다. `빛과 어둠의 세례` 스택이 증가하는 것은 `앱솔루트 킬` 스킬의 속성이라고 생각할 수도 있습니다. 그렇다면 이 동작은 `앱솔루트 킬` 의 동작 과정에 기술되어야 합니다.
    simaple은 Component가 다른 Component의 상태에 직접 접근할 수 있도록 `binds` 속성을 지원합니다. `binds`에 명시된 상태는 reducer가 동작할 때 해당되는 address의 상태값을 Store에 조회하여 지정된 값에 할당합니다. 
    ```python
    component = AttackSkillComponent(
      name="앱솔루트 킬",
      binds={
        ".빛과 어둠의 세례.stack_state": "batism_of_light_and_darkness_stack_state"
      }
    )
    ...
    class AbsoluteKillComponent(AttackSkillComponent):
      ...
      @reducer_method
      def use(self, _, cooltime_state, batism_of_light_and_darkness_stack_state):
        ...
    ```
    이 방법은 필연적으로 새로운 Component class의 작성을 요구하기 때문에 추천되지 않습니다. Reducer의 동작 간의 순서가 보장되어야 하는 경우에만 이같은 방법을 통해 상태를 관리하는 것이 추천됩니다.
    **명심하세요: simaple의 핵심 단위는 상태입니다. Component의 작성 기준은 상태여야 합니다. 한 Component의 상태를 다른 Component에서 참조하는 것은 전혀 권장되지 않습니다**

