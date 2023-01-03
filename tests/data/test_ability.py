from simaple.core.jobtype import JobType
from simaple.data.ability import get_best_ability


def test_get_ability():
    ability = get_best_ability(JobType.archmagefb)
    print(ability)
