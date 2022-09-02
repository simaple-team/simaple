Benchmark
=======

- Provide Standardized item set for fair-comparison between jobs.


Usage
=====

- benchmark는 단일 메서드 build만을 지원합니다.

### using builtin benchmark

- 아래와 같은 Builtin Benchmark를 지원합니다.
  - Epic
  - EpicUnique
  - Unique
  - LegendaryHalf
  - Legendary18
  - Legendary

```python
from simaple.benchmark.interpreter import builtin_blueprint
from simaple.core import JobCategory
from simaple.gear.gear_repository import GearRepository

benchmark = builtin_blueprint("EpicUnique", JobCategory.warrior)
gear_repository = GearRepository()

gearset = user_gearset_blueprint.build(gear_repository)
print(gearset.get_total_stat())
```


- Use builtin
Ideation
=======

- 모든 benchmark는 기본적인 아이템 셋을 가진다.
- 각각의 아이템 셋은 직업간-설정에 의해 override될 수 있다.
- 벤치마크 내에서, 각각의 설정은 몇 개의 간략화된 설정값으로 인해 대치될 수 있어야 한다.
- 각각의 설명은, 간결하게, 필요한 내용을 묘사할 수 있어야 한다.

직업이 제시되면, 그 직업에 대한 아이템 세트를 제공해줄 수 있어야 한다.

