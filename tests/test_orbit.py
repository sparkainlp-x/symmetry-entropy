"""Tests for orbit entropy (symmetry_entropy.orbit).

Ground truth, measured on the real symmetry-quantum-flip-membrane
code: asymmetric bases have orbit 8 (3 bits); blocks has orbit 2
(1 bit); ring and cross have orbit 1 (0 bits). Closed-orbit storage
of the 4 asymmetric bases is 32 distinct patterns. The base-only
equivariance failure is a measured negative result, kept and
asserted -- not hidden.
"""

import math

import pytest

from symmetry_entropy.orbit import (
    BASE_PATTERNS,
    FALSIFIED_PATTERNS,
    OPS,
    HolographicMembrane,
    apply_op,
    closed_orbit_patterns,
    distinct_recalls,
    orbit,
    orbit_entropy,
)


def test_orbit_entropy_asymmetric():
    """Each asymmetric base: orbit 8, entropy log2(8) = 3 bits."""
    for name in ("alpha", "beta", "gamma", "delta"):
        pat = BASE_PATTERNS[name]
        assert len(orbit(pat)) == 8
        assert orbit_entropy(pat) == pytest.approx(3.0, abs=1e-9)


def test_orbit_entropy_blocks():
    """blocks: orbit 2, entropy log2(2) = 1 bit (falsified design)."""
    pat = FALSIFIED_PATTERNS["blocks"]
    assert len(orbit(pat)) == 2
    assert orbit_entropy(pat) == pytest.approx(1.0, abs=1e-9)


def test_orbit_entropy_ring():
    """ring: orbit 1, entropy 0 bits -- the orbit has collapsed."""
    pat = FALSIFIED_PATTERNS["ring"]
    assert len(orbit(pat)) == 1
    assert orbit_entropy(pat) == pytest.approx(0.0, abs=1e-9)


def test_orbit_entropy_cross():
    """cross: orbit 1, entropy 0 bits -- fully symmetric, nothing to tell apart."""
    pat = FALSIFIED_PATTERNS["cross"]
    assert len(orbit(pat)) == 1
    assert orbit_entropy(pat) == pytest.approx(0.0, abs=1e-9)


def test_closed_orbit_total_32():
    """Closed-orbit storage of the 4 asymmetric bases: 32 distinct patterns."""
    patterns = closed_orbit_patterns()
    assert len(patterns) == 32
    assert len(set(patterns.values())) == 32


def test_distinct_recalls_closed_orbit():
    """In closed-orbit mode distinct recalls equal the orbit size.

    The projection resolves exactly as much as the orbit entropy
    allows: 8 for the asymmetric bases, 2 for blocks, 1 for ring/cross.
    """
    patterns = dict(closed_orbit_patterns())
    for name, pat in FALSIFIED_PATTERNS.items():
        for op in OPS:
            patterns[f"{name}@{op}"] = apply_op(pat, op)
    membrane = HolographicMembrane(patterns)
    expected = {"alpha": 8, "beta": 8, "gamma": 8, "delta": 8,
                "blocks": 2, "ring": 1, "cross": 1}
    all_patterns = dict(BASE_PATTERNS)
    all_patterns.update(FALSIFIED_PATTERNS)
    for name, pat in all_patterns.items():
        assert distinct_recalls(membrane, pat) == expected[name]
        assert distinct_recalls(membrane, pat) == len(orbit(pat))


def test_base_only_equivariance_failure():
    """NEGATIVE RESULT, measured: base-only storage is NOT equivariant.

    Recalling the 7 non-identity D4 transforms of each base pattern
    against the base-only membrane (4 patterns) returns the wrong base
    most of the time. Correct counts, measured on the real code:
    alpha 3/7, beta 2/7, gamma 3/7, delta 4/7 (12/28 total). The
    projection cannot resolve the orbit because the orbit was never
    stored -- that is the failure, and it is the point: the orbit
    entropy (3 bits) is exactly the information base-only mode lacks.
    """
    membrane = HolographicMembrane(BASE_PATTERNS)
    expected_correct = {"alpha": 3, "beta": 2, "gamma": 3, "delta": 4}
    total = 0
    for name, pat in BASE_PATTERNS.items():
        correct = sum(
            1 for op in OPS
            if op != "identity"
            and membrane.recall(apply_op(pat, op))[0] == name
        )
        assert correct == expected_correct[name]
        assert correct < 7  # the failure is real for every base
        total += correct
    assert total == 12  # 12/28 transforms recalled correctly, 16 wrong


def test_orbit_is_log2_of_size():
    """orbit_entropy is exactly log2 of the orbit size, for every pattern."""
    all_patterns = dict(BASE_PATTERNS)
    all_patterns.update(FALSIFIED_PATTERNS)
    for pat in all_patterns.values():
        assert orbit_entropy(pat) == pytest.approx(
            math.log2(len(orbit(pat))), abs=1e-12)


def test_orbit_invalid_length():
    with pytest.raises(ValueError):
        orbit((1, -1, 1))
    with pytest.raises(ValueError):
        orbit_entropy((1,) * 15)
