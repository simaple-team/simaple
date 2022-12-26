from simaple.simulate.component.specific.adele import EtherGauge


def test_order_count(adele_store, order):
    adele_store.set_state(
        ".에테르.ether_gauge",
        EtherGauge(
            stack=400,
            maximum_stack=400,
            creation_step=100,
            order_consume=100,
        ),
    )

    order.use(None)
    order.elapse(500)
    order.use(None)
    order.elapse(500)
    order.use(None)

    assert order.running().stack == 6


def test_order_elapse(adele_store, order):
    adele_store.set_state(
        ".에테르.ether_gauge",
        EtherGauge(
            stack=400,
            maximum_stack=400,
            creation_step=100,
            order_consume=100,
        ),
    )

    order.use(None)
    order.elapse(10000)
    order.use(None)
    order.elapse(10000)
    order.use(None)

    order.elapse(20000)
    assert order.running().stack == 4

    order.elapse(10000)
    assert order.running().stack == 2

    order.elapse(10000)
    assert order.running().stack == 0
