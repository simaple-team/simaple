from simaple.wasm.skill import getAllComponent


def test_get_all_component():
    components = getAllComponent()
    assert len(components) > 1

    # every component should have a name and id
    for component in components:
        assert "name" in component
        assert "id" in component
