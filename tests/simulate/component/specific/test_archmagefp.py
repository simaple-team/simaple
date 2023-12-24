from simaple.simulate.component.specific.archmagefb import ( 
    FerventDrain,
    FerventDrainState,
    FerventDrainStack,
) 
from simaple.core import Stat
from typing import Optional


def test_fervent_drain_buff() -> None:
    stack = FerventDrainStack(max_count=10, count=10)
    assert stack.get_buff() == Stat(final_damage_multiplier=50)

def test_fervent_drain_restriction() -> None:
    stack = FerventDrainStack(max_count=5, count=10)
    assert stack.get_buff() == Stat(final_damage_multiplier=25)

    stack.set_max_count(10)
    assert stack.get_buff() == Stat(final_damage_multiplier=50)

    stack.set_max_count(5)
    assert stack.get_buff() == Stat(final_damage_multiplier=25)
