"""Tests for the honeycomb / bee-hexagon extension.

Ground truth measured on the real code (2026-11-15). Four parts:
D6 orbit entropy, honeycomb lattice + Hales efficiency, Shipman
projection geometry, and the radical-pair compass toy.

Honest notes, asserted here too: the isotropic RPM has NO direction
dependence (that limitation is why the anisotropic version exists);
Shipman's correlation is documented but its mechanism is unproven --
this module measures the projection geometry, not the bee's brain.
"""

import math

import pytest

from symmetry_entropy.honeycomb import (
    D6_ALTERNATING,
    D6_ASYMMETRIC,
    D6_HONEYCOMB_CELL,
    D6_ONE_MINUS,
    D6_TWO_ADJACENT_MINUS,
    D6_TWO_OPPOSITE_MINUS,
    HexMembrane,
    d6_closed_orbit_patterns,
    d6_distinct_recalls,
    d6_orbit,
    d6_orbit_entropy,
    honeycomb_patch_bipartite,
    rpm_anisotropic_yield,
    rpm_isotropic_yield,
    rpm_singlet_yield,
    shipman_alpha_curve,
    shipman_arms_at_vertices,
    shipman_transition_alpha,
    tile_perimeter,
)


# ---------------------------------------------------------------------------
# 1. D6 orbit entropy
# ---------------------------------------------------------------------------

def test_d6_orbit_sizes():
    """Orbit sizes measured on the 12 D6 operations."""
    assert len(d6_orbit(D6_ASYMMETRIC)) == 12
    assert len(d6_orbit(D6_ALTERNATING)) == 2
    assert len(d6_orbit(D6_HONEYCOMB_CELL)) == 1
    assert len(d6_orbit(D6_ONE_MINUS)) == 6
    assert len(d6_orbit(D6_TWO_ADJACENT_MINUS)) == 6
    assert len(d6_orbit(D6_TWO_OPPOSITE_MINUS)) == 3


def test_d6_orbit_entropy_values():
    """log2 of the orbit size, in bits."""
    assert d6_orbit_entropy(D6_ASYMMETRIC) == pytest.approx(3.585, abs=1e-3)
    assert d6_orbit_entropy(D6_ALTERNATING) == pytest.approx(1.000, abs=1e-9)
    assert d6_orbit_entropy(D6_HONEYCOMB_CELL) == pytest.approx(0.000, abs=1e-9)
    assert d6_orbit_entropy(D6_ONE_MINUS) == pytest.approx(2.585, abs=1e-3)
    assert d6_orbit_entropy(D6_TWO_ADJACENT_MINUS) == pytest.approx(2.585, abs=1e-3)
    assert d6_orbit_entropy(D6_TWO_OPPOSITE_MINUS) == pytest.approx(1.585, abs=1e-3)


def test_d6_asymmetric_exceeds_d4():
    """A fully asymmetric hexagonal pattern (3.585 bits) beats D4's 3.000 bits.

    The hexagon has more symmetry to break (12 operations vs 8), so
    an asymmetric hexagonal pattern carries more distinguishable
    information than an asymmetric square pattern.
    """
    assert d6_orbit_entropy(D6_ASYMMETRIC) > 3.0
    assert d6_orbit_entropy(D6_ASYMMETRIC) == pytest.approx(math.log2(12), abs=1e-9)


def test_d6_honeycomb_cell_fully_symmetric():
    """The all-+1 honeycomb cell has orbit 1, like the D4 ring.

    Fully symmetric: there is nothing to distinguish, and the
    projection cannot distinguish which transform a probe came from
    -- because there are no distinct transforms.
    """
    assert len(d6_orbit(D6_HONEYCOMB_CELL)) == 1
    assert d6_orbit_entropy(D6_HONEYCOMB_CELL) == 0.0


def test_d6_distinct_recalls_closed_orbit():
    """Distinct recalls equal orbit size in closed-orbit mode (claim e)."""
    for pat, expected in ((D6_ASYMMETRIC, 12), (D6_ALTERNATING, 2),
                          (D6_HONEYCOMB_CELL, 1), (D6_ONE_MINUS, 6),
                          (D6_TWO_OPPOSITE_MINUS, 3)):
        membrane = HexMembrane(d6_closed_orbit_patterns(pat, "hex"))
        assert d6_distinct_recalls(membrane, pat) == expected


# ---------------------------------------------------------------------------
# 2. Honeycomb lattice and Hales efficiency
# ---------------------------------------------------------------------------

def test_honeycomb_patch_is_bipartite():
    """Central hexagon + 6 neighbours: bipartite, 24 vertices, 30 edges, 12/12."""
    patch = honeycomb_patch_bipartite()
    assert patch["bipartite"] is True
    assert patch["n_vertices"] == 24
    assert patch["n_edges"] == 30
    assert len(patch["A"]) == 12
    assert len(patch["B"]) == 12
    assert patch["A"].isdisjoint(patch["B"])
    assert len(patch["A"] | patch["B"]) == 24


def test_hales_perimeters_unit_area():
    """Hexagon has the least perimeter for unit area (Hales 1999)."""
    assert tile_perimeter("hexagon") == pytest.approx(3.7224, abs=1e-3)
    assert tile_perimeter("square") == pytest.approx(4.0000, abs=1e-9)
    assert tile_perimeter("triangle") == pytest.approx(4.5590, abs=1e-3)
    assert tile_perimeter("hexagon") < tile_perimeter("square") < tile_perimeter("triangle")


def test_hales_perimeters_scale_with_area():
    """Perimeter scales as sqrt(area) for every tile shape."""
    for shape in ("hexagon", "square", "triangle"):
        assert tile_perimeter(shape, area=4.0) == pytest.approx(
            2.0 * tile_perimeter(shape, area=1.0), abs=1e-9)


# ---------------------------------------------------------------------------
# 3. Shipman projection geometry
# ---------------------------------------------------------------------------

def test_shipman_transition_alpha():
    """The topology transition is at alpha = 1/sqrt(3) = 0.5774."""
    assert shipman_transition_alpha() == pytest.approx(1.0 / math.sqrt(3.0), abs=1e-9)
    assert shipman_transition_alpha() == pytest.approx(0.5774, abs=1e-3)


def test_shipman_arms_inside_above_transition():
    """For alpha > 1/sqrt(3) the arms stay inside (hit the edges, not the vertices)."""
    for alpha in (2.0, 1.0, 0.8):
        assert shipman_arms_at_vertices(alpha) is False
        curve = shipman_alpha_curve(alpha)
        assert curve["theta_deg"] < 60.0
        # endpoint is strictly inside the circumradius: on an edge, not a vertex
        ex, ey = curve["right_endpoint"]
        assert math.hypot(ex, ey) < 1.0 - 1e-6


def test_shipman_arms_at_vertices_at_and_below_transition():
    """At alpha = 1/sqrt(3) the arms hit the vertices exactly (theta = 60 deg)."""
    curve = shipman_alpha_curve(shipman_transition_alpha())
    assert curve["theta_deg"] == pytest.approx(60.0, abs=1e-9)
    assert curve["at_vertices"] is True
    for end in (curve["left_endpoint"], curve["right_endpoint"]):
        assert math.hypot(end[0], end[1]) == pytest.approx(1.0, abs=1e-9)
    # below the transition the arms have passed the vertex direction
    assert shipman_arms_at_vertices(0.4) is True
    assert shipman_arms_at_vertices(0.2) is True


def test_shipman_curve_endpoints_are_symmetric():
    """The two arms are mirror images about the vertical."""
    curve = shipman_alpha_curve(1.0)
    lx, ly = curve["left_endpoint"]
    rx, ry = curve["right_endpoint"]
    assert lx == pytest.approx(-rx, abs=1e-9)
    assert ly == pytest.approx(ry, abs=1e-9)
    assert len(curve["curve"]) == 50  # 25 samples per arm


# ---------------------------------------------------------------------------
# 4. Radical-pair mechanism (compass toy)
# ---------------------------------------------------------------------------

def test_rpm_isotropic_strength_dependence():
    """Isotropic yield falls with field strength (measured values)."""
    assert rpm_isotropic_yield(0.0) == pytest.approx(0.6250, abs=1e-3)
    assert rpm_isotropic_yield(25e-6) == pytest.approx(0.4179, abs=1e-3)
    assert rpm_isotropic_yield(50e-6) == pytest.approx(0.3876, abs=1e-3)
    assert rpm_isotropic_yield(100e-6) == pytest.approx(0.3795, abs=1e-3)


def test_rpm_isotropic_has_no_direction_dependence():
    """HONEST LIMITATION: the isotropic model cannot be a compass.

    B along z and B along x give the same yield (0.3876 at 50 uT):
    the isotropic hyperfine has no preferred axis, so the yield
    cannot encode direction. That is why the anisotropic version
    exists.
    """
    y_z = rpm_singlet_yield((0.0, 0.0, 50e-6), 1.76e8, 1.76e8, 1.76e8)
    y_x = rpm_singlet_yield((50e-6, 0.0, 0.0), 1.76e8, 1.76e8, 1.76e8)
    assert y_z == pytest.approx(0.3876, abs=1e-3)
    assert y_x == pytest.approx(0.3876, abs=1e-3)
    assert y_z == pytest.approx(y_x, abs=1e-9)


def test_rpm_anisotropic_direction_dependence():
    """Anisotropic yield depends on direction -- that IS the compass signal."""
    assert rpm_anisotropic_yield((0.0, 0.0, 0.0)) == pytest.approx(0.3750, abs=1e-3)
    assert rpm_anisotropic_yield((0.0, 0.0, 50e-6)) == pytest.approx(0.3763, abs=1e-3)
    assert rpm_anisotropic_yield((50e-6, 0.0, 0.0)) == pytest.approx(0.2524, abs=1e-3)
    diag = 50e-6 / math.sqrt(2.0)
    assert rpm_anisotropic_yield((diag, 0.0, diag)) == pytest.approx(0.3135, abs=1e-3)


def test_rpm_direction_contrast_is_the_compass():
    """z vs x at 50 uT differ by 0.124 -- a large, usable contrast."""
    y_z = rpm_anisotropic_yield((0.0, 0.0, 50e-6))
    y_x = rpm_anisotropic_yield((50e-6, 0.0, 0.0))
    assert y_z - y_x == pytest.approx(0.1239, abs=1e-3)
    assert y_z - y_x > 0.1


def test_rpm_yields_are_probabilities():
    """Every singlet yield is a probability in [0, 1]."""
    for b in (0.0, 25e-6, 50e-6, 100e-6, 200e-6):
        assert 0.0 <= rpm_isotropic_yield(b) <= 1.0
        assert 0.0 <= rpm_anisotropic_yield((0.0, 0.0, b)) <= 1.0
        assert 0.0 <= rpm_anisotropic_yield((b, 0.0, 0.0)) <= 1.0


# ---------------------------------------------------------------------------
# Unified claims (e)-(h)
# ---------------------------------------------------------------------------

def test_unified_claims_e_through_h():
    """unified_claim() runs all eight claims; (e)-(h) pass and overall is True."""
    from symmetry_entropy.unified import unified_claim

    result = unified_claim()
    assert result["headline_allowed"] is False
    assert result["overall_pass"] is True
    for key in ("claim_e", "claim_f", "claim_g", "claim_h"):
        assert result[key]["pass"] is True
    # (e): asymmetric hexagonal pattern, 12 recalls = orbit 12 (3.585 bits)
    asym = result["claim_e"]["patterns"]["asymmetric"]
    assert asym["orbit_size"] == 12
    assert asym["distinct_recalls"] == 12
    assert asym["orbit_entropy"] == pytest.approx(3.585, abs=1e-3)
    # (f): hexagon least perimeter, patch bipartite 12/12
    assert result["claim_f"]["least_perimeter_is_hexagon"] is True
    assert result["claim_f"]["patch_bipartite"] is True
    # (g): compass contrast z - x at 50 uT is 0.1239
    assert result["claim_g"]["direction_contrast_z_minus_x"] == pytest.approx(
        0.1239, abs=1e-3)
    # (h): transition at 1/sqrt(3)
    assert result["claim_h"]["transition_alpha"] == pytest.approx(
        1.0 / math.sqrt(3.0), abs=1e-9)
