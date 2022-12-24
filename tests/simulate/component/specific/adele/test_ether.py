from simaple.simulate.component.specific.adele import EtherState


def test_ether_elapse(ether):
    ether.elapse(10020)
    assert ether.running().stack == 5


def test_ether_divide(ether):
    ether.trigger(None)
    assert ether.running().stack == 12


def test_ether_resonance(ether):
    ether.resonance(None)
    assert ether.running().stack == 20


def test_ether_order_consume(adele_store, ether):
    adele_store.set_state(
        ".에테르.ether_state",
        EtherState(
            stack=100,
            maximum_stack=400,
            creation_step=100,
            order_consume=100,
        ),
    )

    ether.order(None)

    assert ether.running().stack == 0
