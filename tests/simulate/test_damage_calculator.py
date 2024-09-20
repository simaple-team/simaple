from simaple.core.base import Stat
from simaple.core.damage import STRBasedDamageLogic
from simaple.simulate.report.base import DamageLog
from simaple.simulate.report.dpm import DamageCalculator
from simaple.simulate.reserved_names import Tag


def test_damage_calculator():
    damage_calc = DamageCalculator(
        character_spec=Stat(
            STR=100, attack_power=10, ignored_defence=100, elemental_resistance=0
        ),
        damage_logic=STRBasedDamageLogic(
            attack_range_constant=1.0,
            mastery=1.0,
        ),
    )

    log = DamageLog(name="test", damage=300, hit=3, buff=Stat(), tag=Tag.DAMAGE)

    assert damage_calc.get_damage(log) == 120 * 3 * 0.5
