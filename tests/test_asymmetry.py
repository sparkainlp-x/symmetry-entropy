"""Tests for asymmetry cost (symmetry_entropy.asymmetry).

Ground truth, measured on the Pauli group {I, X} on 1 qubit:
|0> has orbit {|0>, |1>}, size 2; the twirl is I/2, S = 1 bit, cost
= 1 bit = log2(2). |+> is fixed by X, orbit size 1; the twirl is
|+><+|, S = 0, cost = 0 bits = log2(1). This mirrors ring (0 bits)
vs an asymmetric pattern (3 bits): a state already symmetric under
the group costs nothing to symmetrize, because there is nothing to
distinguish and nothing to destroy.
"""

import math

import numpy as np
import pytest

from symmetry_entropy.asymmetry import (
    KET_ONE,
    KET_PLUS,
    KET_ZERO,
    PAULI_GROUP_IX,
    PAULI_I,
    PAULI_X,
    asymmetry_cost,
    ket_to_dm,
    state_orbit_size,
    twirl,
    von_neumann_entropy,
)


def test_von_neumann_entropy_pure_zero():
    """Pure states have entropy 0."""
    for psi in (KET_ZERO, KET_ONE, KET_PLUS):
        assert von_neumann_entropy(ket_to_dm(psi)) == pytest.approx(0.0, abs=1e-9)


def test_von_neumann_entropy_maximally_mixed():
    """I/2 has entropy 1 bit."""
    assert von_neumann_entropy(np.eye(2, dtype=complex) / 2) == pytest.approx(1.0, abs=1e-9)


def test_twirl_zero_is_maximally_mixed():
    """Twirling |0> under {I, X} gives I/2 (the orbit average)."""
    rho = ket_to_dm(KET_ZERO)
    twirled = twirl(rho, PAULI_GROUP_IX)
    assert twirled == pytest.approx(np.eye(2, dtype=complex) / 2, abs=1e-9)
    assert von_neumann_entropy(twirled) == pytest.approx(1.0, abs=1e-9)


def test_asymmetry_cost_zero():
    """|0>: cost 1 bit = log2(orbit size 2)."""
    rho = ket_to_dm(KET_ZERO)
    assert asymmetry_cost(rho, PAULI_GROUP_IX) == pytest.approx(1.0, abs=1e-9)
    assert asymmetry_cost(rho, PAULI_GROUP_IX) == pytest.approx(
        math.log2(state_orbit_size(KET_ZERO, PAULI_GROUP_IX)), abs=1e-9)


def test_asymmetry_cost_one():
    """|1>: same orbit as |0>, cost 1 bit."""
    rho = ket_to_dm(KET_ONE)
    assert asymmetry_cost(rho, PAULI_GROUP_IX) == pytest.approx(1.0, abs=1e-9)
    assert state_orbit_size(KET_ONE, PAULI_GROUP_IX) == 2


def test_asymmetry_cost_plus():
    """|+>: cost 0 bits = log2(orbit size 1). Mirrors ring (0 bits)."""
    rho = ket_to_dm(KET_PLUS)
    assert asymmetry_cost(rho, PAULI_GROUP_IX) == pytest.approx(0.0, abs=1e-9)
    assert state_orbit_size(KET_PLUS, PAULI_GROUP_IX) == 1
    assert twirl(rho, PAULI_GROUP_IX) == pytest.approx(rho, abs=1e-9)


def test_asymmetry_cost_nonnegative():
    """The twirl never lowers entropy (data-processing inequality)."""
    rng = np.random.default_rng(42)
    for _ in range(10):
        v = rng.normal(size=2) + 1j * rng.normal(size=2)
        rho = ket_to_dm(v)
        assert asymmetry_cost(rho, PAULI_GROUP_IX) >= -1e-12


def test_state_orbit_sizes():
    """Orbit sizes under {I, X}: |0> and |1> move, |+> is fixed."""
    assert state_orbit_size(KET_ZERO, PAULI_GROUP_IX) == 2
    assert state_orbit_size(KET_ONE, PAULI_GROUP_IX) == 2
    assert state_orbit_size(KET_PLUS, PAULI_GROUP_IX) == 1


def test_twirl_is_idempotent():
    """Twirling twice changes nothing: the twirl is a projection."""
    rho = ket_to_dm(KET_ZERO)
    once = twirl(rho, PAULI_GROUP_IX)
    twice = twirl(once, PAULI_GROUP_IX)
    assert twice == pytest.approx(once, abs=1e-9)


def test_von_neumann_entropy_rejects_bad_rho():
    with pytest.raises(ValueError):
        von_neumann_entropy(np.eye(2, dtype=complex))  # trace 2, not 1
    with pytest.raises(ValueError):
        von_neumann_entropy(np.array([[1.0, 1.0], [0.0, 0.0]], dtype=complex))  # not Hermitian


def test_twirl_rejects_empty_group():
    with pytest.raises(ValueError):
        twirl(ket_to_dm(KET_ZERO), [])
