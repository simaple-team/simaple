*****************************
About Simulation: Tutorial
*****************************

.. contents:: Contents
    :local:


Introduction
==============

simaple에서 여러분은 스킬을 정의하고, 정의된 스킬을 활용하여 시뮬레이션을 수행할 수 있습니다. 이것은 우리가 원하는 모든 것이죠; 완벽한 인게임 시뮬레이션 말입니다.
이 장에서, 우리는 ``아크메이지 불/독`` 의 시뮬레이션을 만들어보게 됩니다! 본 튜토리얼의 내용을 바탕으로, 여러분은 원하는 직업의 시뮬레이션을 적절한 방식으로 구성하고,
동작시켜볼 수 있습니다. 보다 고급 기능이 필요하다면, 고급 기능 안내 문서를 참조하세요.

시작하기
========

시뮬레이션을 구현하기 위해서 우리는 먼저 우리가 사용 가능한 스킬들의 묶음을 정의해야 합니다.
그리고, 그 스킬의 사용 결과를 대상 캐릭터의 성능을 바탕으로 데미지로 변환시켜 해석해야 할 것입니다.


스킬셋 정의하기
===================

simaple에서 사용 가능한 스킬 묶음은 Client라고 불립니다. get_client 메서드를 통해 Client를 생성할 수 있습니다. 

.. code-block:: python

    from simaple.simulate.kms import get_client
    from simaple.data.client_configuration import get_client_configuration
    from simaple.core.jobtype import JobType
    from simaple.core import ActionStat, Stat

    client_configuration = get_client_configuration(JobType.archmagefb)
    character_stat = Stat(
        INT=4932.0,
        INT_multiplier=573.0,
        INT_static=15460.0,
        magic_attack=2075.0,
        magic_attack_multiplier=81.0,
        critical_rate=100.0,
        critical_damage=83.0,
        boss_damage_multiplier=144.0,
        damage_multiplier=167.7,
        final_damage_multiplier=110.0,
        ignored_defence=95,
    )
        
    action_stat = ActionStat(buff_duration=185)

    client = get_client(
        action_stat,
        client_configuration.get_groups(),
        {
            "character_stat": character_stat,
            "character_level": 260,
            "weapon_attack_power": 789,
            "weapon_pure_attack_power": 500,
        },
        client_configuration.get_filled_v_skill(30),
        client_configuration.get_filled_v_improvements(60),
        combat_orders_level=1,
        passive_skill_level=0,
    )


코드가 정말 길고 복잡합니다! 하지만 안타깝게도 이것이 여러분이 클라이언트를 구성하기 위해 제공해야 하는 최소한의 정보입니다.
각각의 요소와 그것들의 의미에 대해, 여러분이 지금 당장 자세히 알 필요는 없습니다. 우리가 알아야 하는 사항에 대해서만 알아봅시다.

- ``get_client_configuration`` 는 여러분이 관심있어하는 직업에 관한 정보를 손쉽게 다루게 해줍니다. ``client_configuration`` 객체가 여러분이 다루고자 하는 직업에 관련된 복잡한 일을 대신 해줄 겁니다.
- ``ActionStat`` 과 ``Stat`` 은 내가 시뮬레이션하고자 하는 캐릭터의 스텟 상태를 나타냅니다. ``character_stat`` 에 나의 stat 정보가 오게 되겠죠? ``ActionStat`` 은 버프 지속시간, 소환수 지속시간과 같은 정보가 포함되는 객체입니다. 본문에서는 버프 지속 시간만 185%로 설정했습니다.

- 세 번째 인자는 조금 복잡한데, 여기에는 여러분이 시뮬레이션을 동작시키기 위해 제공해주어야 하는 추가적인 정보가 요구됩니다. 여러분은 반드시, 아래와 같은 값을 제공해주어야 합니다.

  - ``character_stat`` : 이 값은 대상 캐릭터의 스텟입니다.
  - ``character_level`` : 캐릭터의 레벨입니다.
  - ``weapon_attack_power`` : 여러분 무기의 공격력(법사 직업군은 마력)입니다.
  - ``weapon_pure_attack_power`` : 여러분 무기의 순수 공격력(법사 직업군은 마력)입니다.

- ``get_client`` 는 네 번째 인자로 5차 스킬의 레벨 정보를 요구합니다. 이 데이터를 수동으로 입력하는건 상당히 귀찮은 일이므로, 앞에서 정의한 ``client_configuration`` 을 통해 손쉽게 생성합시다. ``client_configuration.get_filled_v_skill(30)`` 는 여러분의 직업의 5차 스킬들이 모두 30레벨인 상태로 초기화되도록 합니다.
- 이와 유사하게, ``get_client`` 는 다섯 번째 인자로 5차 강화코어로 인한 4차 이하 스킬들의 강화 정보를 요구합니다. ``client_configuration.get_filled_v_improvements(60)`` 는 여러분의 직업의 강화 코어로 인한 4차 이하 스킬들이 모두 60레벨의 강화 효과를 받도록 합니다.
- ``combat_orders_level`` 은 컴뱃 오더스의 레벨, ``passive_skill_level`` 은 어빌리티 내 패시브 스킬 레벨 1 증가 옵션의 여부입니다.

이러한 정보가 제공되었을때, ``get_client`` 함수는 ``Client`` 객체를 반환합니다. 
축하합니다! 우리는 이제 우리가 사용하고자하는 스킬들이 모두 정의된 ``Client`` 를 생성했습니다. 


Policy 구현하기
==============

우리는 앞선 내용을 통해, 우리가 시뮬레이션하고자 하는 환경을 만들었습니다. 이제 이 환경에서 **어떻게** 시뮬레이션해야 할 지 이야기할 시간입니다.
어떻게 동작할지 정의된 모듈을 simaple에서는 ``Policy`` 라고 부릅니다. simaple은 모든 직업에 대해 굉장히 단순하게 동작하는 ``DefaultOrderPolicy`` 를 제공합니다. ``client_configuration`` 을 통해 이를 생성해 봅시다.

.. code-block:: python

    ...

    client_configuration = get_client_configuration(JobType.archmagefb)
    policy = client_configuration.get_default_policy()


이제 우리는 Client도 있고, Policy도 있습니다. 이제 시뮬레이션을 수행해 보죠!


시뮬레이션 수행하기
===========================

시뮬레이션을 앞서 만든 client와 Policy를 통해 작동시켜봅시다. 50초동안 시뮬레이션을 동작시켜 보죠. 아래와 같은 코드를 입력해주세요. 앞의 코드에서 이어진다는 사실을 명심하세요!


.. code-block:: python

    ...
    from simaple.simulate.policy import get_shell

    shell = get_shell(archmagefb_client)

    while client.environment.show("clock") < 50_000:
        shell.exec_policy(policy, early_stop=50_000)

총 시뮬레이션 시간은 ``client.environment.show("clock")`` 을 통해 얻을 수 있습니다. 시간이 다할때까지, 우리는 policy의 결정을 받아와서, shell을 거쳐 client에 전달합니다.
그런데, 시뮬레이션이 동작했지만, 시뮬레이션의 결과를 볼 방법이 없네요. simaple은 동작 분석을 위해 아래의 두 가지 개념을 추적할 방법을 제공합니다.

- 매 순간, Policy가 행동하기로 한 결정 (Operation History)
- 매 순간, Policy의 결정으로 인해 발생한 피해량 (Report)

이 두가지를 한 번 기록해 보겠습니다. 위 코드를 아래 코드로 대체해 주세요.


.. code-block:: python

    ...

    from simaple.simulate.report.base import Report, ReportEventHandler
    from simaple.simulate.policy import get_shell

    report = Report()
    client.add_handler(ReportEventHandler(report))

    shell = get_shell(client)

    while client.environment.show("clock") < 50_000:
        shell.exec_policy(policy, early_stop=50_000)
    
    shell.history.dump("history.log")


``shell.history`` 는 우리의 시뮬레이션 과정에서 Policy의 결정, 즉 Operation을 기록합니다. ``history.dump`` 를 통해, 손쉽게 history를 저장할 수 있습니다.
코드가 수행된 이후 history.log를 열어보세요. 지금 당장은 이해할 수 없을지도 모르지만, 스킬의 이름과 그것들을 언제 use했는지 묘사되어 있을겁니다.

``report`` 는 그 순간 발생한 피해량에 관한 정보를 담고 있습니다. 우리가 ``add_handler`` 를 통해 report를 client에 등록함으로서, 시뮬레이션 과정에서 발생한 모든 피해량은 Report 객체에 저장됩니다.
``len(report)`` 를 수행해서, report에 실제로 데이터가 쌓여있는지 확인해 보세요. 동작 시간을 변경하고, 실제로 report에 길이가 바뀌는지 확인해 보아도 좋습니다.
작성된 리포트는 ``report.save`` 를 통해 저장할 수 있습니다. ``report.save("report.tsv")`` 를 수행하고, ``report.tsv`` 파일을 열어 확인해보세요.


피해량 계산하기
=========================

우리는 성공적으로 시뮬레이션을 수행하고, 결과를 얻었습니다. 이제 남은 작업은 결과 처리뿐이죠. 결과 처리라 함은, 데미지 결과물을 가지고 통계를 내거나, 그래프를 그리거나, DPM(damage-per-minute)를 구하는 행위 모두를 포함합니다.
simaple은 피해 로그에 데미지가 담겨있지 않습니다. 피해 로그를 데미지로 바꾸기 위해서는 DamageCalculator를 선언해야 합니다.


.. code-block:: python

    ...

    from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage
    from simaple.data.damage_logic import get_damage_logic

    damage_calculator = DamageCalculator(
        character_spec=character_stat,
        damage_logic=get_damage_logic(JobType.archmagefb, combat_orders_level=1),
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
    )


데미지를 계산하기 위해서는 참으로 많은 정보가 필요합니다. 먼저 계산하고자하는 대상 캐릭터의 스텟 정보(character_stat) 가 요구됩니다.
`damage_logic` 은 피해량 계산 방식을 인자로 받습니다. `get_damage_logic` 함수를 호출하여 직업에 알맞은 피해 계산 로직을 선택합니다. 이로 인해 우리는 주스텟이 INT이고, 마력을 사용하며, 부스텟이 LUK이고, 무기상수가 1.2인 피해량 계산 방식을 사용하게 됩니다.
방어율도 명시해주어야겠죠. ``armor=300`` 을 통해 방어율 300임을 명시합니다.
level_advantage와 force_advantage는 각각 레벨과 포스 차이에서 오는 피해량 증가량으로, 실수값을 전달받습니다. 다만, 레벨 어드밴티지는 계산이 까다로우니 LevelAdvantage 를 호출하여 계산하는 것이 추천됩니다.


이제 마지막입니다! 이렇게 생성한 damage_calculator로 dpm을 계산해보죠. 계산은 한 번에 이루어집니다.

.. code-block:: python

    ...

    print(f"{damage_calculator.calculate_dpm(report):,}")

우리의 시뮬레이션 과정에서 계산된 분당 피해량이 출력되었을 것입니다.


마지막으로, 우리가 작성해온 코드를 모두 모아보겠습니다. 모여있는 코드를 보고, 각각의 과정에 대해 다시 한 번 돌이켜보세요. import는 모아서 맨 위로 올려도 괜찮습니다.

.. code-block:: python

    from simaple.simulate.kms import get_client
    from simaple.data.client_configuration import get_client_configuration
    from simaple.core.jobtype import JobType
    from simaple.core import ActionStat, Stat

    ## Declare Client
    client_configuration = get_client_configuration(JobType.archmagefb)
    character_stat = Stat(
        INT=4932.0,
        INT_multiplier=573.0,
        INT_static=15460.0,
        magic_attack=2075.0,
        magic_attack_multiplier=81.0,
        critical_rate=100.0,
        critical_damage=83.0,
        boss_damage_multiplier=144.0,
        damage_multiplier=167.7,
        final_damage_multiplier=110.0,
        ignored_defence=95,
    )
    action_stat = ActionStat(buff_duration=185)

    client = get_client(
        action_stat,
        client_configuration.get_groups(),
        {
            "character_stat": character_stat,
            "character_level": 260,
            "weapon_attack_power": 789,
            "weapon_pure_attack_power": 500,
        },
        client_configuration.get_filled_v_skill(30),
        client_configuration.get_filled_v_improvements(60),
        combat_orders_level=1,
        passive_skill_level=0,
    )

    ## Declare Policy

    client_configuration = get_client_configuration(JobType.archmagefb)
    policy = client_configuration.get_default_policy()

    ## Run simulation

    from simaple.simulate.report.base import Report, ReportEventHandler
    from simaple.simulate.policy import get_shell

    report = Report()
    client.add_handler(ReportEventHandler(report))

    shell = get_shell(client)

    while client.environment.show("clock") < 50_000:
        shell.exec_policy(policy, early_stop=50_000)
    
    shell.history.dump("history.log")

    from simaple.simulate.report.dpm import DamageCalculator, LevelAdvantage
    from simaple.data.damage_logic import get_damage_logic

    ## Calculate DPM

    damage_calculator = DamageCalculator(
        character_spec=character_stat,
        damage_logic=get_damage_logic(JobType.archmagefb, combat_orders_level=1),
        armor=300,
        level_advantage=LevelAdvantage().get_advantage(250, 260),
        force_advantage=1.5,
    )

    print(f"{damage_calculator.calculate_dpm(report):,}") # Our simulation's DPM
