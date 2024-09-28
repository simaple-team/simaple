from simaple.request.adapter.union_loader.adapter import (
    get_union_squad,
    get_union_squad_effect,
)


def test_union_raiders_response(character_union_raiders_response):
    union_squad = get_union_squad(character_union_raiders_response)
    squad_effect = get_union_squad_effect(character_union_raiders_response)

    assert union_squad.get_stat().short_dict() == squad_effect.stat.short_dict()
