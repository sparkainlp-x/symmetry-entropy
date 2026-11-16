# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

"""Tests for the self-determinism factor D.

Ground truth measured on the real vendored code (2026-11-15).
D is the fraction of a probe the projection determines by itself:
D = <psi|P|psi> for the quantum membrane, max |overlap|^2 for the
classical membrane. D = 1: fully self-determined. D = 0: kernel
(invisible). 0 < D < 1: partial.
"""

import math

import pytest

from symmetry_entropy.orbit import (
    BASE_PATTERNS,
    FALSIFIED_PATTERNS,
    HolographicMembrane as ClassicalMembrane,
    apply_op,
    closed_orbit_patterns,
)
from symmetry_entropy.projection_entropy import (
    HolographicMembrane as QuantumMembrane,
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
from symmetry_entropy.self_determinism import (
    classical_self_determinism,
    self_determinism_factor,
    self_determinism_gap,
)
from symmetry_entropy.unified import _closed_orbit_membrane_all


@pytest.fixture(scope="module")
def qmem():
    return QuantumMembrane([bell_phi_plus(), bell_phi_minus(), bell_psi_plus()])


@pytest.fixture(scope="module")
def cmem_closed():
    return _closed_orbit_membrane_all()


@pytest.fixture(scope="module")
def cmem_base():
    return ClassicalMembrane(dict(BASE_PATTERNS))


def test_quantum_clean_stored_is_fully_self_determined(qmem):
    """Phi+ clean: D = 1.0 -- the probe is entirely in the stored subspace."""
    assert self_determinism_factor(qmem, bell_phi_plus()) == pytest.approx(1.0, abs=1e-9)
    assert self_determinism_factor(qmem, bell_phi_minus()) == pytest.approx(1.0, abs=1e-9)
    assert self_determinism_factor(qmem, bell_psi_plus()) == pytest.approx(1.0, abs=1e-9)


def test_quantum_kernel_is_zero(qmem):
    """Psi- (orthogonal to all stored): D = 0.0 -- the system determines nothing."""
    assert self_determinism_factor(qmem, bell_psi_minus()) == pytest.approx(0.0, abs=1e-9)
    assert is_kernel(qmem, bell_psi_minus())
    assert born_weights(qmem, bell_psi_minus()) == [0.0, 0.0, 0.0]


def test_quantum_noisy_decreases(qmem):
    """Noise pushes the probe out of the stored subspace, so D falls."""
    d_025 = self_determinism_factor(qmem, noisy(bell_phi_plus(), 0.25, 11))
    d_075 = self_determinism_factor(qmem, noisy(bell_phi_plus(), 0.75, 11))
    assert d_025 == pytest.approx(0.843355, abs=1e-3)
    assert d_075 == pytest.approx(0.567154, abs=1e-3)
    assert 1.0 > d_025 > d_075 > 0.0


def test_quantum_haar_random(qmem):
    """Random states have part of their norm in the kernel; D varies by draw."""
    assert self_determinism_factor(qmem, random_state(2, 7)) == pytest.approx(0.909800, abs=1e-3)
    assert self_determinism_factor(qmem, random_state(2, 42)) == pytest.approx(0.192721, abs=1e-3)
    ds = [self_determinism_factor(qmem, random_state(2, s)) for s in range(200)]
    assert all(0.0 <= d <= 1.0 for d in ds)
    # Stored subspace is 3 of 4 dims, so the mean over random draws is
    # near 3/4 (measured 0.7197 over 200 seeds).
    assert abs(sum(ds) / len(ds) - 0.7197) < 1e-3


def test_quantum_d_is_the_born_weight_denominator(qmem):
    """D = sum |m|^2: the total Born weight before normalisation.

    The Born weights are |m|^2 / D, so D is the denominator of the
    weights and the projection entropy is the entropy of the
    normalised weights. D says how much the system can see;
    projection entropy says how uncertain the answer is given that.
    """
    probe = noisy(bell_phi_plus(), 0.25, 11)
    d = self_determinism_factor(qmem, probe)
    total = sum(abs(m) ** 2 for m in qmem.overlaps(probe))
    assert d == pytest.approx(total, abs=1e-9)
    weights = born_weights(qmem, probe)
    assert abs(sum(weights) - 1.0) < 1e-9
    assert projection_entropy(qmem, probe) == pytest.approx(0.618, abs=1e-3)


def test_quantum_d_one_means_certain_projection(qmem):
    """D = 1 and projection entropy 0 go together for a clean stored probe."""
    probe = bell_phi_plus()
    assert self_determinism_factor(qmem, probe) == pytest.approx(1.0, abs=1e-9)
    assert projection_entropy(qmem, probe) == pytest.approx(0.0, abs=1e-9)


def test_quantum_gap_complements_d(qmem):
    """gap = 1 - D: 0 for a stored probe, 1 for the kernel."""
    assert self_determinism_gap(qmem, bell_phi_plus()) == pytest.approx(0.0, abs=1e-9)
    assert self_determinism_gap(qmem, bell_psi_minus()) == pytest.approx(1.0, abs=1e-9)


def test_classical_closed_orbit_is_fully_self_determined(cmem_closed):
    """Every transform of a stored pattern has D = 1 in closed-orbit mode."""
    for name, pat in list(BASE_PATTERNS.items()) + list(FALSIFIED_PATTERNS.items()):
        for op in ("identity", "rot90", "rot180", "rot270",
                   "flip_h", "flip_v", "transpose", "anti_transpose"):
            assert classical_self_determinism(cmem_closed, apply_op(pat, op)) == pytest.approx(
                1.0, abs=1e-9)


def test_classical_base_only_lacks_orbit_information(cmem_base):
    """A transformed probe in base-only mode has D < 1: the orbit was never stored.

    alpha rot90: best overlap with a base pattern is 0.5, squared 0.25.
    That missing 0.75 is exactly the orbit information base-only lacks --
    the same lack behind the 12/28 equivariance failure.
    """
    assert classical_self_determinism(cmem_base, BASE_PATTERNS["alpha"]) == pytest.approx(1.0, abs=1e-9)
    assert classical_self_determinism(cmem_base, apply_op(BASE_PATTERNS["alpha"], "rot90")) == pytest.approx(0.25, abs=1e-9)
    assert classical_self_determinism(cmem_base, apply_op(BASE_PATTERNS["alpha"], "rot180")) == pytest.approx(0.25, abs=1e-9)


def test_classical_d_in_unit_interval(cmem_closed, cmem_base):
    """D is in [0, 1] for every probe in both modes."""
    probes = [BASE_PATTERNS["alpha"], apply_op(BASE_PATTERNS["beta"], "rot270"),
              FALSIFIED_PATTERNS["ring"], FALSIFIED_PATTERNS["blocks"]]
    for mem in (cmem_closed, cmem_base):
        for probe in probes:
            d = classical_self_determinism(mem, probe)
            assert 0.0 <= d <= 1.0
