import pytest


def test_ether_elapse(ether):
    ether.elapse(10020)
    assert ether.running().stack == 5


def test_ether_divide(ether):
    ether.trigger(None)
    assert ether.running().stack == 12


def test_ether_resonance(ether):
    ether.resonance(None)
    assert ether.running().stack == 20


def test_ether_order_consume(ether):
    ether.resonance(None)  # 20
    ether.resonance(None)  # 40
    ether.resonance(None)  # 60
    ether.resonance(None)  # 80
    ether.resonance(None)  # 100
    ether.order(None)  # 0
    assert ether.running().stack == 0
