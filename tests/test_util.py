import time

from simaple.util import Timer


def test_timer():
    with Timer():
        time.sleep(0.1)
