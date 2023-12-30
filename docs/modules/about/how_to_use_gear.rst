*****************************
About: Gear
*****************************

.. contents:: Contents
    :local:


이 문서에서는 simaple에서 장비를 정의하는 Gear를 생성하는 방법에 대해 다룹니다.


Declaring Gear
======================

simaple에서, 장비 아이템은 ``simaple.gear.gear.Gear`` class를 통해 정의할 수 있습니다.
Gear class는 단순히, 장비 아이템에 대한 속성을 모아둔 값 객체에 불과합니다. Gear class의 생성자는 다음과 같습니다.

.. code-block:: python
    
    class Gear(BaseModel):
        meta: GearMeta
        stat: Stat
        scroll_chance: int
        potential: Potential = Field(default_factory=Potential)
        additional_potential: Potential = Field(
            default_factory=Potential
        )

        class Config:
            extra = Extra.forbid
            validate_assignment = True
            allow_mutation = False


강화되지 않은 하이네스 던위치햇을 생성하고 싶다면, 다음과 같이 호출하게 될 것입니다.

.. code-block:: python
    
    gear = Gear(
        meta=GearMeta(
            id=1005568,
            base_stat=Stat(
                LUK=40,
                INT=40,
                ignored_defence=10,
                MHP=360,
                MMP=360
            ),
            name="하이네스 던위치햇",
            type=GearType.cap,
            req_level=150,
            max_scroll_chance=11,
            boss_reward=True,
            superior_eqp=False,
            req_job=2, ## mage 
            set_item_id=248, ## rootabyss mage set
            joker_to_set_item=False,
        )
        stat=Stat(
            LUK=40,
            INT=40,
            ignored_defence=10,
            MHP=360,
            MMP=360
        ),
        scroll_chance=11,
        potential=Potential(options=[]), 
        additional_potential=Potential(options=[])
    )

아이템을 정의하기 위해서 아이템의 정보를 담고 있는 ``GearMeta`` 객체를 생성하여 넘겨주어야 한다는 점을 확인할 수 있었을 것입니다.
매번 아이템의 정의를 게임 내에서 확인하고, 일일이 값을 대입하여 생성하는 것은 굉장히 피곤한 작업입니다.
simaple은 게임 내에 정의된 대부분의 장비 아이템을 생성하여 제공해주는 ``GearRepository`` 를 제공합니다. 따라서, 위 코드를 호출하는 대신 GearRepository의 메서드를 호출하여 쉽게 GearMeta를 생성할 수 있습니다.

.. code-block:: python
    
    from simaple.gear.gear_repository import GearRepository

    repository = GearRepository()
    gear_meta = repository.get_gear_meta(1005568) ## Same as above
    
    gear = Gear(
        meta=gear_meta,
        stat=gear_meta.base_stat,
        scroll_chance=11,
        potential=Potential(options=[]), 
        additional_potential=Potential(options=[])
    )

강화가 전혀 적용되지 않은 장비아이템은 ``GearRepository`` 의 ``get_by_name`` 혹은 ``get_by_id`` 로 손쉽게 얻을 수도 있습니다.


.. code-block:: python
    
    from simaple.gear.gear_repository import GearRepository

    repository = GearRepository()
    gear = repository.get_by_id(1005568) ## Same as above
    gear = repository.get_by_name("하이네스 던위치햇") ## Same as above


Modifing Gear
=================

게임 내에서, 우리는 아무런 강화가 되지 않은 아이템을 착용하지 않습니다. 우리는 다양한 강화 시스템을 통해 아이템을 보다 나은 상태로 변경합니다.
우리는 Gear의 setter method를 통해, 강화가 적용된 아이템을 쉽게 얻을 수 있습니다. 15의 힘을 추가하는 강화는 다음과 같이 표현됩니다.

.. code-block:: python

    gear = repository.get_by_name("하이네스 던위치햇")
    upgraded_gear = gear.add_stat(Stat(STR=15))
    assert gear.stat != upgraded_gear

위에 전시된 Gear의 코드에서 확인할 수 있듯이, Gear는 불변 객체입니다. 이는 여러분이 어떤 정의된 Gear 객체에 변경을 시도하면 실패한다는 것을 의미합니다. 따라서, gear의 모든 메서드는 자신의 속성을 바꾸는 대신 변환된 gear를 반환한다는 사실에 유의하세요.

유사한 방법을 통해, 잠재능력 및 에디셔널 잠재능력 또한 재설정할 수 있습니다. 모든 메서드는 새로운 Gear 객체를 반환한다는 점에 유의하세요.

.. code-block:: python

    gear = gear.set_potential(Potential(options=[
        Stat(INT_multiplier=6),
        Stat(INT_multiplier=3),
        Stat(INT_multiplier=3),
    ]))
    gear = gear.set_additional_potential(Potential(options=[
        Stat(magic_attack=12),
        Stat(INT_multiplier=4),
    ]))

gear 객체는 불변이기때문에, 모든 강화 효과는 항상 새로운 gear 객체를 생성한다는 점에 유의하세요.

Improvements
===================

Gear는 ``add_stat`` 메서드만을 제공하지만, 우리가 사용하는 강화 시스템은 일반적으로 한정되어 있습니다. 
메이플스토리 내에는 스타포스, 주문의 흔적, 그리고 추가옵션이라는 세 가지의 아이템 스텟 강화 방식이 존재합니다.
이들 강화 시스템으로 상승하는 스텟의 양은 고정되어 있습니다; 예를 들어, 150제 아이템의 스텟 추가옵션이 +1일수는 없습니다.
특정 강화 시스템에 의한 스텟 상승량을 손쉽게 계산하기 위하여, simaple은 Improvements module을 제공합니다.

각각의 Improvements는 제공된 ``GearMeta`` 정보와, 직전의 아이템 스텟 정보 ``ref_stat`` 을 인자로 요구합니다. ``ref_stat`` 은 스타포스 계산을 제외하는 경우 제공되지 않아도 괜찮습니다.


Scroll
------
Scroll Improvement는 단순한 wrapper입니다. Scroll은 제공된 Stat을 Improvement로 반환합니다.


.. code-block:: python

    ...    
    from simaple.gear.improvements.scroll import Scroll

    scroll = Scroll(stat=Stat(STR=15), name="any-scroll-name")
    assert scroll.calculate_improvement(gear.meta) == Stat(STR=15)


SpellTrace
----------
주문서 강화와 다르게, 주문의 흔적을 통한 강화 시스템은 적용 가능한 상승 수치가 한정적입니다. 
한정적인 수치를 쉽게 얻기 위해, SpellTrace Improvement는 제시된 확률과 스텟 종류에 따른 강화 수치를 제공합니다.

.. code-block:: python

    ...    
    from simaple.gear.improvements.spell_trace import SpellTrace
    from simaple.core import StatProps

    gear = repository.get_by_name("하이네스 던위치햇")
    spell_trace = SpellTrace(probability=30, stat_prop_type=StatProps.INT)
    assert scroll.calculate_improvement(gear.meta) == Stat(INT=7, MHP=120)

    gear = repository.get_by_name("앱솔랩스 메이지글러브")
    spell_trace = SpellTrace(probability=30, stat_prop_type=StatProps.INT)
    assert scroll.calculate_improvement(gear.meta) == Stat(magic_attack=3)


Starforce
----------
simaple은 스타포스 강화에 따른 상승 수치를 쉽게 계산할 수 있는 Starforce Improvement class또한 제공합니다.
Starforce는 ref_stat을 요구합니다.

.. code-block:: python

    ...    
    from simaple.gear.improvements.starforce import Starforce

    gear = repository.get_by_name("하이네스 던위치햇")
    starforce = Starforce(star=17)
    assert starforce..calculate_improvement(gear.meta, gear.meta.base_stat) == Stat(INT=62, LUK=62, attack_power=19, magic_attack=19, MHP=255)


Bonus(추가옵션)
----------------
simaple은 제시된 등급에 해당되는 추가옵션을 계산하는 Bonus class를 제공합니다.

.. code-block:: python

    ...    
    from simaple.gear.improvements.bonus import DualStatBonus

    gear = repository.get_by_name("하이네스 던위치햇")
    bonus = DualStatBonus(stat_type_pair=[BaseStatType.INT, BaseStatType.LUK], grade=6)
    assert bonus.calculate_improvement(gear.meta) == Stat(INT=24, LUK=24)


또는 일일이 대응되는 class를 import하는 대신에, Factory class를 사용할 수도 있습니다.

.. code-block:: python

    ...    
    from simaple.gear.bonus_factory import BonusFactory, BonusType

    gear = repository.get_by_name("하이네스 던위치햇")
    bonus = BonusFactory().create(BonusType.INT_LUK, 6)
    assert bonus.calculate_improvement(gear.meta) == Stat(INT=24, LUK=24)

gear는 단순한 Value-Object이기 때문에, 동일한 강화 효과를 중복으로 적용하는 것에 대한 어떠한 제약조건도 존재하지 않습니다. 이는 아래와 같은 동작이 허용됨을 의미합니다.

.. code-block:: python
        
    ...
    starforce = Starforce(star=15, enhancement_type="Starforce")
    gear = gear.add_stat(starforce.calculate_improvement(gear))
    gear = gear.add_stat(starforce.calculate_improvement(gear))  # 어떤 오류도 발생하지 않습니다!

Gear class는 단순히 장비아이템의 현재 상태를 묘사합니다. 따라서, 여러분은 Gear class를 사용함에 있어, 이것이 어떠한 validation을 수행해 줄 것을 기대해서는 안됩니다. 


Create gear with GearBlueprint
==============================

많은 경우, 우리는 장비 아이템을 묘사함에 있어, 그것이 가지고 있는 스텟만을 묘사하기 보다는, 장비 아이템에 적용된 모든 강화 효과에 대해 알고 있기를 바랍니다.
예를 들어, 어떤 아이템에 대해 우리는 22성 30% 주흔작 아이템이라고 보통 언급할 뿐, 주스텟 227에 공격력 95인 아이템이라고 이야기하는 경우는 드뭅니다.
``Gear`` class는 장비 아이템에 적용된 강화 효과의 목록을 기억하지 않기 때문에, 객체를 생성하기에는 편리하지만, 장비 그 자체를 표현하기에는 표현력이 부족합니다.

장비에 적용된 강화 효과를 기술하고, 그로부터 ``Gear`` 객체를 만들기 위해 우리는 ``GearBlueprint`` 를 사용할 수 있습니다.

.. code-block:: python

    from simaple.gear.blueprint.gear_blueprint import PracticalGearBlueprint, BonusSpec
    from simaple.gear.bonus_factory import BonusType

    blueprint = PracticalGearBlueprint(
        meta=gear_repository.get_gear_meta(1005568),
        spell_trace=SpellTrace(probability=30, stat_prop_type=StatProps.INT),
        star=17,
        bonuses=[
            BonusSpec(bonus_type=BonusType.INT_LUK, grade=6),
            BonusSpec(bonus_type=BonusType.all_stat_multiplier, grade=6)
        ]
        potential=Potential(),
        additional_potential=Potential(),
    )

    gear = blueprint.build() # 30% 주흔작, 17성, 추옵 올텟6/int24/luk24

GearBlueprint는 Gear 내에서 존재하는 각각의 강화 시스템을 올바른 순서로 적용하기 때문에, 앞서 제기되었던 동일한 강화 방식이 여러번 적용될 수 있는 경우와 같은 이슈를 방지할 수 있습니다.

보다 구체적으로 이야기해서, 게임 내에 존재하는 강화 시스템을 활용하여 장비를 구성하고 싶다면 항상 GearBlueprint를 사용하는 것이 추천됩니다. Gear class를 직접 다루는 것은 다른 방법으로 아이템을 생성하고자 할 때만 사용하세요.

Appendix. handling potential
=================================

Gear 또는 GearBlueprint에서, 잠재능력 및 에디셔널 잠재능력은 potential / additional_potential field를 통해 정의됩니다.
다른 강화 속성과 달리, 잠재능력은 Gear의 stat에 합산되지 않음에 유의하세요.

Gear의 잠재능력은 set_potential 또는 set_additional_potential 메서드 호출을 통해 변경할 수 있으며, 다른 함수 호출과 마찬가지로 변경이 적용된 새로운 Gear를 반환합니다.

GearBlueprint는 mutable object이므로, 직접 속성 치환을 통해 잠재능력 값을 설정 또는 변경할 수 있습니다.

Potential 및 Potential은 options를 통해 값을 전달받습니다. options Field에는 Stat, ActionStat 또는 LevelStat이 올 수 있습니다.
두 class의 options는 반드시 길이가 3일 필요는 없습니다. 해당 필드는 임의 길이의 list를 허용합니다.


.. code-block:: python

    from simaple.gear.potential import Potential
    from simaple.core import Stat, ActionStat, LevelStat

    potential = Potential(options=[
        Stat(INT_multiplier=12),
        ActionStat(cooltime_reduce=2),
        LevelStat(),
    ])

    additional_potential = Potential(options=[
        Stat(INT_multiplier=7),
    ])

뿐만 아니라, Potential class는 어떠한 종류의 값 검증도 수행하지 않습니다. 따라서, 여러분은 잠재능력을 설정하기 전에, 해당 값이 사용 가능한 값인지 충분히 검증한 상태여야 합니다.




