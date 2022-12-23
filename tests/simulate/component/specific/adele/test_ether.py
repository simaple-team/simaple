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
