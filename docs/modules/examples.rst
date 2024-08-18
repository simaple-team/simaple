**************************
Examples
**************************

.. contents:: Contents
    :local:


Benchmark Example
=================

Benchmark는 제시된 직업에 알맞은, 설정된 장비 수준의 ``Geatset`` 을 불러옵니다.


아래와 같은 Builtin Benchmark를 지원합니다.

- Epic
- EpicUnique
- Unique
- LegendaryHalf
- Legendary18
- Legendary


Create Gearset From Baseline
-----------------------------

::

    from simaple.data.baseline import get_baseline_gearset
    from simaple.core import JobCategory
    from simaple.gear.gear_repository import GearRepository

    gearset = get_baseline_gearset("EpicUnique", JobCategory.warrior)
    print(gearset.get_total_extended_stat().stat.show())
