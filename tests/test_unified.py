"""Tests for the unified claim (symmetry_entropy.unified).

The three falsifiable statements, with their measured numbers:
(a) distinct recalls equal orbit size in closed-orbit mode;
(b) the projection kernel (Psi-) is invisible, all weights 0;
(c) the projected world has higher entropy than the underlying state
by the asymmetry cost, in the classical orbit case AND the quantum
twirl case. No headline claim is emitted: headline_allowed is False.
"""

import pytest

from symmetry_entropy.unified import unified_claim


@pytest.fixture(scope="module")
def claim():
    return unified_claim()


def test_unified_structure(claim):
    assert claim["version"] == "0.1.0"
    assert claim["headline_allowed"] is False
    assert "headline_note" in claim
    assert set(claim) >= {"claim_a", "claim_b", "claim_c", "overall_pass"}


def test_unified_claim_a_numbers(claim):
    """(a) Distinct recalls = orbit size, for every pattern."""
    expected = {
        "alpha": (8, 3.0, 8), "beta": (8, 3.0, 8),
        "gamma": (8, 3.0, 8), "delta": (8, 3.0, 8),
        "blocks": (2, 1.0, 2), "ring": (1, 0.0, 1), "cross": (1, 0.0, 1),
    }
    for name, (size, ent, rec) in expected.items():
        row = claim["claim_a"]["patterns"][name]
        assert row["orbit_size"] == size
        assert row["orbit_entropy"] == pytest.approx(ent, abs=1e-9)
        assert row["distinct_recalls"] == rec
        assert row["pass"] is True
    assert claim["claim_a"]["pass"] is True


def test_unified_claim_b_kernel(claim):
    """(b) Psi- is invisible: all Born weights 0, is_kernel True."""
    row = claim["claim_b"]
    assert row["weights"] == [0.0, 0.0, 0.0]
    assert row["is_kernel"] is True
    assert row["projection_entropy"] == pytest.approx(0.0, abs=1e-9)
    assert row["pass"] is True


def test_unified_claim_c_classical(claim):
    """(c) Classical: gap = orbit entropy (alpha 3 bits, ring 0 bits)."""
    alpha = claim["claim_c"]["classical"]["alpha"]
    assert alpha["underlying_entropy"] == pytest.approx(0.0, abs=1e-9)
    assert alpha["projected_entropy"] == pytest.approx(3.0, abs=1e-9)
    assert alpha["gap"] == pytest.approx(3.0, abs=1e-9)
    assert alpha["orbit_entropy"] == pytest.approx(3.0, abs=1e-9)
    assert alpha["pass"] is True
    ring = claim["claim_c"]["classical"]["ring"]
    assert ring["gap"] == pytest.approx(0.0, abs=1e-9)
    assert ring["orbit_entropy"] == pytest.approx(0.0, abs=1e-9)
    assert ring["pass"] is True


def test_unified_claim_c_quantum(claim):
    """(c) Quantum: cost = log2(orbit size) (|0> 1 bit, |+> 0 bits)."""
    zero = claim["claim_c"]["quantum"]["|0>"]
    assert zero["S_rho"] == pytest.approx(0.0, abs=1e-9)
    assert zero["S_twirl"] == pytest.approx(1.0, abs=1e-9)
    assert zero["asymmetry_cost"] == pytest.approx(1.0, abs=1e-9)
    assert zero["log2_orbit_size"] == pytest.approx(1.0, abs=1e-9)
    assert zero["pass"] is True
    plus = claim["claim_c"]["quantum"]["|+>"]
    assert plus["asymmetry_cost"] == pytest.approx(0.0, abs=1e-9)
    assert plus["log2_orbit_size"] == pytest.approx(0.0, abs=1e-9)
    assert plus["pass"] is True


def test_unified_overall_pass(claim):
    assert claim["claim_c"]["pass"] is True
    assert claim["overall_pass"] is True


def test_no_headline(claim):
    """No headline claim is emitted, ever."""
    assert claim["headline_allowed"] is False
