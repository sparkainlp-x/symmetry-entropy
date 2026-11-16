# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

"""Tests for projection entropy (symmetry_entropy.projection_entropy).

Ground truth, measured on the real quantum-projection code (stored
Phi+, Phi-, Psi+; 3 patterns; max projection entropy log2(3) = 1.585
bits). Clean weights and entropies are asserted to 1e-9; noisy and
random cases to 1e-3 (they are rounded to 3 decimals in the report).
The kernel case (Psi-, orthogonal to all stored patterns) is a
negative result, kept and asserted: all weights 0, invisible to the
projection.
"""

import math

import pytest

from symmetry_entropy.projection_entropy import (
    HolographicMembrane,
    bell_phi_minus,
    bell_phi_plus,
    bell_psi_minus,
    bell_psi_plus,
    born_weights,
    is_kernel,
    noisy,
    projection_entropy,
    random_state,
)


@pytest.fixture(scope="module")
def membrane():
    return HolographicMembrane(
        [bell_phi_plus(), bell_phi_minus(), bell_psi_plus()])


def test_born_weights_phi_plus_clean(membrane):
    """Clean stored Phi+: weights [1, 0, 0], entropy 0 bits (certain)."""
    weights = born_weights(membrane, bell_phi_plus())
    assert weights == [1.0, 0.0, 0.0]
    assert projection_entropy(membrane, bell_phi_plus()) == pytest.approx(0.0, abs=1e-9)


def test_projection_entropy_noisy_025(membrane):
    """Phi+ at noise sigma 0.25, seed 11: 0.618 bits."""
    probe = noisy(bell_phi_plus(), 0.25, 11)
    weights = born_weights(membrane, probe)
    assert weights == pytest.approx([0.872, 0.113, 0.015], abs=1e-3)
    assert projection_entropy(membrane, probe) == pytest.approx(0.618, abs=1e-3)


def test_projection_entropy_noisy_075(membrane):
    """Phi+ at noise sigma 0.75, seed 11: 1.270 bits."""
    probe = noisy(bell_phi_plus(), 0.75, 11)
    weights = born_weights(membrane, probe)
    assert weights == pytest.approx([0.474, 0.465, 0.061], abs=1e-3)
    assert projection_entropy(membrane, probe) == pytest.approx(1.270, abs=1e-3)


def test_projection_entropy_random_seed7(membrane):
    """Haar-random 2-qubit state, seed 7: 1.581 bits (near the max)."""
    probe = random_state(2, 7)
    weights = born_weights(membrane, probe)
    assert weights == pytest.approx([0.315, 0.368, 0.317], abs=1e-3)
    assert projection_entropy(membrane, probe) == pytest.approx(1.581, abs=1e-3)


def test_projection_entropy_random_seed42(membrane):
    """Haar-random 2-qubit state, seed 42: 1.375 bits."""
    probe = random_state(2, 42)
    weights = born_weights(membrane, probe)
    assert weights == pytest.approx([0.199, 0.204, 0.597], abs=1e-3)
    assert projection_entropy(membrane, probe) == pytest.approx(1.375, abs=1e-3)


def test_kernel_psi_minus(membrane):
    """NEGATIVE RESULT, measured: Psi- is invisible to the projection.

    Psi- is orthogonal to every stored pattern, so every overlap is 0,
    every Born weight is 0, and is_kernel is True. The projection has
    no answer for it -- not a wrong answer, no answer. This is the
    kernel of the stored subspace: the part of the space the projection
    cannot see.
    """
    probe = bell_psi_minus()
    weights = born_weights(membrane, probe)
    assert weights == [0.0, 0.0, 0.0]
    assert is_kernel(membrane, probe) is True
    assert projection_entropy(membrane, probe) == pytest.approx(0.0, abs=1e-9)


def test_projection_entropy_bounded_by_log2_n(membrane):
    """Projection entropy never exceeds log2(3) = 1.585 bits (3 patterns)."""
    max_ent = math.log2(3)
    probes = [bell_phi_plus(), bell_phi_minus(), bell_psi_plus(),
              bell_psi_minus(), random_state(2, 7), random_state(2, 42),
              noisy(bell_phi_plus(), 0.75, 11)]
    for probe in probes:
        assert projection_entropy(membrane, probe) <= max_ent + 1e-9


def test_projection_entropy_grows_with_noise(membrane):
    """More noise -> more projection entropy (same probe, same seed)."""
    e0 = projection_entropy(membrane, bell_phi_plus())
    e25 = projection_entropy(membrane, noisy(bell_phi_plus(), 0.25, 11))
    e75 = projection_entropy(membrane, noisy(bell_phi_plus(), 0.75, 11))
    assert e0 < e25 < e75


def test_is_kernel_false_for_stored(membrane):
    for probe in (bell_phi_plus(), bell_phi_minus(), bell_psi_plus()):
        assert is_kernel(membrane, probe) is False
