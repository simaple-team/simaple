from simaple.core import Stat
from simaple.data.doping import get_normal_doping


def test_normal_doping_data():
    normal_doping = get_normal_doping()
    assert isinstance(normal_doping, Stat)
    assert normal_doping != Stat()
