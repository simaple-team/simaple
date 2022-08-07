import pytest

from simaple.gear.util import GearIDCodec


@pytest.mark.parametrize(
    "embedding, expected_gear_id",
    [("KEOEJHME", 1162025), ("KEOHJGHJ", 1152198), ("KEODIGKI", 1113149)],
)
def test_codec(embedding, expected_gear_id):
    codec = GearIDCodec()

    gear_id = codec.decode(embedding)
    assert expected_gear_id == gear_id
    assert embedding == codec.encode(gear_id)
