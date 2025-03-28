************************************
About Simulation: An Explanation
************************************

.. contents:: Contents
    :local:


Introduction
============

simaple의 궁극적인 목적은 완전한 인-게임 시뮬레이션입니다. 
이것은 굉장히 달성하기 어려운 목표입니다. 게임 내 스킬들의 동작 메커니즘은 우리가 어렴풋이 추론하는 것보다 훨씬 복잡합니다. 이를 잘 정제되지 않은 코드로 묘사하고자 했다가는 통제할 수 없는 코드 간 의존성과 테스트 불가능한 오류에 휩싸이게 되기 마련입니다.

simulate 모듈은 이러한 복잡한 스킬간 상호작용을 Redux Pattern을 활용하여 묘사한 라이브러리 입니다.


Why Redux?
===========

simulate 모듈은 Redux Pattern을 사용하여 전체 시스템을 묘사하고 시뮬레이션을 동작시킵니다.

스킬에서부터 생각해봅시다. 스킬들은 보통 상태를 가지고 있습니다. 쿨다운이 대표적인 스킬의 상태죠. 스킬에 관련된 행동을 취하면 상태가 변경됩니다. 스킬을 누르면, 스킬이 사용되고, 쿨다운이 돌게 됩니다. 시간이 자니면 스택이 쌓이고, 쿨다운이 감소할 것입니다. 일부 스킬은 다른 스킬과 상호작용하여 상태가 바뀌기도 합니다. 

이것은 action-state에 매칭될 수 있습니다. 우리가 취하는 행동이 Action에 대응되고, 각 스킬의 상태는 State에 저장되어 있는 셈입니다.
스킬들이 각각 상태를 가지고 있고, 그 상태들이 빈번히 변경된다면, 우리는 각 상태를 store에 위임하여 Redux Pattern을 써볼 수 있습니다.


모든 상태는 Store에 저장됩니다. 
상태는 dispatcher에 의해서 변경될 수 있습니다.
simaple은 스킬을, State를 변경시키는 메서드의 집합으로 간주합니다. 이를 표현하기위해 Component class를 제공합니다.
Component는 동일한 값을 참조하는 dispatcher의 집합입니다. 이것은 게임 내에서의 스킬 객체 하나에 대응될 수 있습니다.

모든 연산 흐름은 상태를 기준으로 설계됩니다. 
예시로, A 스킬이 B 스킬의 쿨타임을 변경하는 경우를 생각해 봅시다. 이 때 행위의 주체는 A 스킬의 트리거이지만, 실제로 변경되는 것은 B스킬의 상태입니다. 따라서 이 트리거는 B 스킬의 상태 기술에 작성되게 됩니다.
이것은 얼핏 느끼기에 부당하게 여겨집니다; 액션의 사용이 완결된 이후 그 결과가 다른 스킬에 영향을 미치는 것이 자연스럽습니다. 그러나 이것은 단일 액션이 여러 차례의 연쇄를 거쳐 상태를 변경하는 동작을 야기합니다. 우리는 다음 원칙을 고수합니다.

``하나의 액션으로 야기되는 상태 변화는 한 번에 일어난다``

하나의 액션이 여러 차례의 상태 변화를 야기하는 논리 흐름은 시스템을 제어하는 ``Player`` 입장에서 시스템에 대한 이해를 어렵게 합니다. ``Player`` 는 스스로의 동작이 어떤 부수-효과를 일으킬지 예측하지 못하게 됩니다. 모든 in-system action dispatching은 단일 액션 처리에 국한되어야 하며 Event의 Action으로의 재해석은 반드시 ``Player`` 에 의해서 통제되어야 합니다.


Description
===============

Action
-------
모든 사용자의 행동은 Action에 대응됩니다. 시뮬레이션은 사용자가 하나의 Action을 생성하여 제공하는것으로부터 시작됩니다.
Action은 게임 내에서 캐릭터에게 내리는 명령에 대응됩니다. 특정 스킬을 누르거나, 특정 시간동안 행동 없이 대기하는 것이 Action이 됩니다.
Action은 name, method, payload의 속성을 가집니다. 이들에 대한 설명은 reducer에서 언급됩니다.

Event
-------

``Event`` 는 ``Action`` 으로 인한 결과입니다. ``Event`` 는 ``Action`` 으로 인해 발생한 delay, damage와 같은 처리가 필요한 것과, 특정 스킬의 실행 사실을 안내하는 로깅 목적의 Event로 크게 나눌 수 있습니다. Event는 반드시 처리될 필요는 없습니다; delay event를 참조하여 전체 시스템의 시간을 경과시키는 것 이외에 그 어떤 이벤트도 필수적으로 처리될 필요는 없어야 합니다.
경과시간 이벤트는 이벤트 중에서 유일하게 처리를 요구하는 ``Event`` 입니다. 이는 ``Player`` 가 스킬 캔슬 등을 통해 명시된 delay 이하의 시간많은 적용할 수 있도록 하기 위함입니다.

State
-------
``State`` 는 묘사하고자 하는 캐릭터의 스킬들이 가지고 있는 상태를 의미합니다. 일반적으로, ``Action`` 은 ``State`` 를 변경시킨 후 ``Event`` 를 발생시킵니다. ``State`` 들을 통해 ``Action`` 에 의해 변경되어야 하는 모든 정보를 담고 있어야 합니다. 반대로, 어떠한 상태도 ``State`` 이외의 방법을 통해 모델링 되어 ``Action`` 에 의해 변경되면 안됩니다.

Entity
-------
simaple은 ``State`` 를 ``Entity`` 의 집합으로 정의합니다. ``Entity`` 는 고유의 성질을 갖추고 있는 상태를 구성하는 최소 단위입니다. 예를 들어, 일반적인 버프 스킬은 지속시간과 쿨다운을 가집니다. 이들 각각은 코드 상에서 ``Cooldown`` 과 ``Duration`` Entity로 모델링 됩니다. 그리고, 이 버프 스킬의 ``State`` 는 아래와 같이 정의됩니다.

.. code-block:: python
    
    class Cooldown(Entity):
        ...

    class Duration(Entity):
        ...

    class BuffSkillState(State):
        cooldown: Cooldown
        duration: Duration



Store
-------

Store는 시스템 내의 **모든** ``State`` 가 저장된 공간입니다. Single-source-of-truth 에 입각하여, 모든 상태는 Store로부터 얻어질 수 있어야 합니다.

Dispatcher
------------

Dispatcher는 상태를 변화시키는 방법에 대한 기술입니다. 위에서 안내된 정의 덕분에, 모든 상태를 변화시키는 행동은 아래와 같은 인터페이스를 가질 것입니다. 이를 Dispatcher라고 부릅니다.
``(Store, Action) -> (Event)``
Dispatcher의 정의는 아름답지는 않습니다; Dispatcher는 분명히 상태를 변화시키지만, 그것은 인자로 받은 Store를 변경함을 의미합니다. 뿐만 아니라, Dispatcher는 Store 내 State의 immutability를 보장하지도 않습니다.

Reducer
----------

Dispatcher는 비-일급 함수라는 nature때문에, 개발자에게 노출되는 인터페이스로는 적절하지 않습니다. 따라서, simaple은 Reducer라는 일급 함수 인터페이스를 제공하여 개발자로 하여 직관적이고 sustainable한 코드를 작성하도록 지원합니다.
Reducer는 아래와 같은 signature를 가지는 함수입니다.
``(Any, State) -> (State, list[Event])``
Reducer는 일급 함수입니다; 이는 제공된 상태가 Reducer로 인해 변하지 않아야 함을 의미합니다. Reducer는 내부적으로 ``ReducerMethodWrappingDispatcher`` 를 통해 Dispatcher로 감싸져, 동작으로 인해 실제로 상태가 변화되게 됩니다.

Reducer는 일급 함수이지만, 그 구성이 복잡합니다. 이러한 복잡함은 simaple이 다중 상태변화 시스템을 지원하기 위함입니다. 하지만 개발자 입장에서 위의 규칙을 전부 준수하면서 Reducer를 추가하는 것은 매우 불편하고 어렵습니다. 따라서 개발자는 Component를 통해 손쉽게 Reducer를 구현하고 이를 Dispatcher로 감싸게 됩니다.

Component
----------

``Component`` 는 simaple simulation의 핵심입니다. ``Component`` 가 가지는 인스턴스 메서드들은 ``@reducer_method`` 로 decorate됨으로서 reducer로 손쉽게 변환됩니다.

간단한 예시를 살펴봅니다.

.. code-block:: python

    ## 1. Define State
    class AttackSkillState(ReducerState):
        cooldown: Cooldown
        dynamics: Dynamics

    class AttackSkillComponent(Component, InvalidatableCooldownTrait, UseSimpleAttackTrait):
        ## 2. Define constructor
        name: str
        damage: float
        hit: float
        cooldown: float = 0.0
        delay: float

        ## 3. Define state initializer
        def get_default_state(self):
            return {
                "cooldown": Cooldown(time_left=0),
            }

        ## 4. A reducer
        @reducer_method
        def elapse(self, time: float, state: AttackSkillState) -> tuple[AttackSkillComponent, list[Event]]:
            return self.elapse_simple_attack(time, state)

        @reducer_method
        def use(self, _: None, state: AttackSkillState) -> tuple[AttackSkillComponent, list[Event]]:
            return self.use_simple_attack(state)

        def _get_simple_damage_hit(self) -> tuple[float, float]:
            return self.damage, self.hit


Component는 크게 네 부분으로 이루어집니다.

먼저, Component가 사용할 State를 정의합니다. State는 ``ReducerState`` 를 상속받아야 합니다. 이 때 정의된 상태는 Component의 리듀서를 정의할 때 사용됩니다.

두번째로, Component의 생성자를 정의합니다. Component 는 ``pydantic.BaseModel`` 을 상속받기 때문에 ``pydantic.BaseModel`` 의 생성자 정의 방식을 활용하여 컴포넌트가 정의되기 위해 필요한 정보를 명시합니다.
자세한 용법은 ``pydantic.BaseModel`` 의 문서를 참조합니다.

세번째로, ``get_default_state`` 를 정의합니다. 모든 ``Component`` 는 해당 메서드를 정의해야 하는데, 이는 Component에 정의된 Reducer들이 인자로 받아가는 ``Entity`` 가 존재하지 않을 때 초기값을 지정하여 전달해주기 위함입니다. 여기서 사용되는 key는 앞서 정의한 상태 ``AttackSkillState`` 의 변수명과 일치해야 합니다. 그렇지 않다면, 프로그램은 당신이 제공한 초기값이 어떤 항목에 해당하는지 찾을 수 없을 것입니다.

마지막으로, ``@reducer_method`` 로 장식된 메서드들이 정의됩니다. 이 함수의 ``signature`` 에 주목하십시오. 이들이 바로 우리가 찾던 리듀서입니다.
``elapse`` 메서드는 두번째 인자로 ``state: AttackSkillState`` 를 받고 있습니다. 이 시그니처는 임의로 선택된 값이 아닙니다. 이는 우리의 상태값이 Store 내에서 ``AttackSkillState`` 형태로 반환되어야 함을 명시합니다. 내부 구현은 이 시그니처를 바탕으로, Store에 적절히 질의하여 해당되는 State를 조합해 넘겨줄 것입니다.
함수의 시그니처가 정확히 Reducer와 일치함에 주목하세요. 이 함수는 정확히 리듀서에 해당합니다!

이같은 기술 방식은, 하나의 Component가, 특정 State들에 연관된 Action을 한데 모아서 잘 정의되도록 합니다. 
이는 게임에서 하나의 **스킬** 에 해당합니다; 즉, 우리는 ``Component`` 를 통해 스킬 객체를 가독성있게, 유지보수 가능하게 관리하기 위함입니다.
스킬의 상태와 스킬에 속하는 리듀서들이 강하게 결합되어, 일종의 클러스터를 형성한다는 사실을 리마인드하십시오.


Component간의 연계
----------------------

때때로, 스킬은 다른 스킬과 상호작용합니다. 이들은 다른 스킬이 발동되었을 때 자신의 이벤트를 발생시키거나, 상태를 변경해야 합니다. 
``빛과 어둠의 세례`` 스택이 증가하는 것은 ``앱솔루트 킬`` 스킬의 속성이라고 생각할 수 있습니다. 그렇다면 이 동작은 ``앱솔루트 킬`` 의 동작 과정에 기술되어야 합니다.
simaple은 Component가 다른 Component의 상태에 직접 접근할 수 있도록 ``binds`` 속성을 지원합니다. ``binds`` 에 명시된 상태는 reducer가 동작할 때 해당되는 address의 상태값을 Store에 조회하여 지정된 값에 할당합니다. 

.. code-block:: python

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
