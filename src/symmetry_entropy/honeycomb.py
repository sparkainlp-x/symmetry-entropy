# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

"""Honeycomb / bee-hexagon extension: D6 symmetry, Hales efficiency,
Shipman projection, and the radical-pair compass.

New in this package (extension, v0.1.0). This is the fifth quantity
family, alongside orbit entropy, projection entropy, asymmetry cost,
and the self-determinism factor. It extends the D4 symmetry of
orbit.py to the hexagon (D6, 12 operations) and connects the
hexagonal geometry to three documented facts: Hales' honeycomb
conjecture, Shipman's flag-manifold correlation with the honeybee
waggle dance, and the radical-pair mechanism of bee magnetoreception.

Definitions
-----------
1. D6 symmetry. A hexagonal pattern is a 6-tuple in {-1, +1}, one
   value per vertex of a hexagonal ring. The dihedral group D6 (12
   operations: 6 rotations, 6 reflections) acts on it.
   d6_orbit_entropy(pattern) = log2(|orbit|) in bits. A fully
   asymmetric hexagonal pattern has orbit 12 (3.585 bits) -- larger
   than D4's 3.000 bits, because the hexagon has more symmetry to
   break. The all-+1 honeycomb cell has orbit 1 (0.000 bits), like
   the D4 ring: fully symmetric, nothing to distinguish.

2. Honeycomb lattice and Hales efficiency. A honeycomb patch (one
   central hexagon plus its 6 neighbours) is a bipartite graph: its
   vertices split into two triangular sublattices A and B, exactly
   like graphene's two sublattices. For unit area, the hexagon has
   the least perimeter (3.7224) of the three regular tilings --
   square 4.0000, equilateral triangle 4.5590. Thomas Hales proved
   in 1999 that the regular hexagon is the most efficient tiling.
   The bee minimises wax; the quantum material's honeycomb symmetry
   protects its Dirac points. Same shape, same reason (optimisation),
   different physics.

3. Shipman projection. Barbara Shipman (University of Rochester)
   found that the 6-dimensional flag manifold -- a quantum geometry
   used for quarks -- projects to a 2-dimensional HEXAGON, and that
   curves in the flag manifold, projected onto that hexagon,
   reproduce the honeybee waggle dance. A variable alpha reproduces
   the whole dance; at alpha = 1/sqrt(3) the curve family changes
   topology, analogous to the dance switching from waggle to circle.
   Covered in Discover, November 1997 (Adam Frank).

   HONEST FRAMING (read this before using the functions): Shipman's
   correlation is DOCUMENTED but the mechanism is UNPROVEN. In the
   20 years since, she published no further papers on it, no other
   academics continued it, and one entomologist called it
   "ridiculous". This module measures the PROJECTION GEOMETRY -- a
   6D object projecting to a 2D hexagon, and an alpha-parameter
   curve family with a topology transition at alpha = 1/sqrt(3) --
   NOT the bee's brain. It does NOT claim bees see 6D space, and it
   does NOT claim the dance IS a quantum projection. The geometry is
   measured; the bee's mechanism is not.

4. Radical-pair mechanism (RPM). Two electron spins S1, S2 (1/2)
   plus one nuclear spin I (1/2) coupled to S1. The Hamiltonian is
   H = gamma*(B.S1 + B.S2) + (Ax*S1x*Ix + Ay*S1y*Iy + Az*S1z*Iz),
   with gamma = 1.76085963e11 rad/s/T. The initial state is the
   electron singlet with a maximally mixed nucleus. The singlet
   yield is Phi_S = k * int_0^inf P_S(t) exp(-k t) dt, computed by
   exact diagonalisation. The yield depends on the field STRENGTH
   (isotropic case) and on the field DIRECTION (anisotropic case) --
   that direction dependence IS the compass signal, and it is the
   leading mechanism for bee magnetoreception (cryptochrome).

   HONEST FRAMING: this is a TOY model (one nucleus, simplified
   hyperfine). It demonstrates the compass PRINCIPLE; it is NOT a
   measurement of a real bee's cryptochrome, which has many nuclei
   and a complex environment. The experimental context is Oesterle
   et al. 2026 (two-photon imaging of the bee anterior optic
   tubercle; a platform for testing the RPM in honeybees).
"""

import math
from collections import deque

import numpy as np

# ---------------------------------------------------------------------------
# 1. D6 symmetry on 6-tuples (hexagonal ring)
# ---------------------------------------------------------------------------

D6_ASYMMETRIC = (1, 1, -1, 1, -1, -1)
D6_ALTERNATING = (1, -1, 1, -1, 1, -1)
D6_HONEYCOMB_CELL = (1, 1, 1, 1, 1, 1)
D6_ONE_MINUS = (1, 1, 1, 1, 1, -1)
D6_TWO_ADJACENT_MINUS = (1, 1, 1, 1, -1, -1)
D6_TWO_OPPOSITE_MINUS = (1, 1, -1, 1, 1, -1)


def _check_hex_pattern(pattern):
    if len(pattern) != 6 or any(x not in (-1, 1) for x in pattern):
        raise ValueError("hexagonal pattern must be 6 cells in {-1, +1}")
    return tuple(pattern)


def d6_rot(pattern, k):
    """Rotate a 6-tuple by k steps: new[i] = old[(i-k) % 6]."""
    p = _check_hex_pattern(pattern)
    return tuple(p[(i - k) % 6] for i in range(6))


def d6_refl(pattern, k):
    """Reflect then rotate by k steps: new[i] = rot(p,k)[(-i) % 6]."""
    r = d6_rot(pattern, k)
    return tuple(r[(-i) % 6] for i in range(6))


def d6_orbit(pattern):
    """Set of distinct D6 transforms of a 6-tuple (12 operations)."""
    p = _check_hex_pattern(pattern)
    return {d6_rot(p, k) for k in range(6)} | {d6_refl(p, k) for k in range(6)}


def d6_orbit_entropy(pattern):
    """log2 of the D6 orbit size, in bits.

    Fully asymmetric: log2(12) = 3.585 bits -- larger than D4's 3.000
    bits, because the hexagon has more symmetry to break. Honeycomb
    cell (all +1): log2(1) = 0 bits, like the D4 ring.
    """
    return math.log2(len(d6_orbit(pattern)))


def d6_hex_overlap(a, b):
    """Normalised overlap of two 6-tuples, in [-1, 1]."""
    if len(a) != 6 or len(b) != 6:
        raise ValueError("hexagonal patterns must have exactly 6 cells")
    return sum(x * y for x, y in zip(a, b)) / 6.0


class HexMembrane:
    """Outer-product memory over named 6-tuples (hexagonal ring).

    Same pattern as orbit.py's HolographicMembrane, but for 6-cell
    patterns instead of 16-cell patterns. Recall uses overlaps,
    which are exactly the normalised projection onto stored patterns.
    """

    def __init__(self, patterns):
        self.patterns = {}
        for name, pat in patterns.items():
            self.patterns[name] = _check_hex_pattern(pat)
        self.matrix = [[0.0] * 6 for _ in range(6)]
        for pat in self.patterns.values():
            for i in range(6):
                for j in range(6):
                    self.matrix[i][j] += pat[i] * pat[j]

    def overlaps(self, probe):
        probe = _check_hex_pattern(probe)
        return {name: d6_hex_overlap(probe, pat)
                for name, pat in self.patterns.items()}

    def recall(self, probe):
        """Return (best_name, best_overlap, all_overlaps). No gate here."""
        ov = self.overlaps(probe)
        best = max(ov, key=lambda k: ov[k])
        return best, ov[best], ov


def d6_closed_orbit_patterns(pattern, name="hex"):
    """All 12 D6 transforms of a pattern, named ``name@op``."""
    p = _check_hex_pattern(pattern)
    out = {}
    for k in range(6):
        out[f"{name}@rot{k}"] = d6_rot(p, k)
        out[f"{name}@refl{k}"] = d6_refl(p, k)
    return out


def d6_distinct_recalls(membrane, pattern):
    """Number of distinct recalls across the D6 orbit, in closed-orbit mode.

    Each distinct transform of the pattern is recalled against the
    membrane; the return value is how many distinct stored names come
    back. In closed-orbit mode this equals the orbit size: the
    projection resolves exactly as much as the orbit entropy allows.
    """
    names = set()
    for transformed in d6_orbit(pattern):
        name, _, _ = membrane.recall(transformed)
        names.add(name)
    return len(names)


# ---------------------------------------------------------------------------
# 2. Honeycomb lattice (bipartite) and Hales efficiency
# ---------------------------------------------------------------------------

def _hexagon_vertices(cx, cy):
    """The 6 vertices of a pointy-top hexagon (circumradius 1).

    Vertex k is at (sin(k*60 deg), cos(k*60 deg)) from the centre, so
    vertex 0 is at the top. Consistent with the Shipman section below.
    """
    return [(cx + math.sin(math.radians(60 * k)),
             cy + math.cos(math.radians(60 * k))) for k in range(6)]


def honeycomb_patch_bipartite():
    """A honeycomb patch (central hexagon + its 6 neighbours) as a graph.

    Returns a dict with the two triangular sublattices A and B (sets
    of vertex coordinates), a bipartite flag, and the vertex/edge
    counts. The patch has 24 vertices and 30 edges, split 12/12
    between the sublattices -- the same bipartite structure as
    graphene (two interpenetrating triangular sublattices).
    """
    centers = [(0.0, 0.0)]
    for k in range(6):
        a = math.radians(60 * k)
        centers.append((math.sqrt(3) * math.cos(a),
                        math.sqrt(3) * math.sin(a)))
    key_to_pt = {}

    def _key(pt):
        return (round(pt[0], 9), round(pt[1], 9))

    edges = set()
    for cx, cy in centers:
        vs = _hexagon_vertices(cx, cy)
        for i in range(6):
            a, b = vs[i], vs[(i + 1) % 6]
            ka, kb = _key(a), _key(b)
            key_to_pt[ka] = a
            key_to_pt[kb] = b
            edges.add((min(ka, kb), max(ka, kb)))
    verts = set(key_to_pt)
    adj = {v: set() for v in verts}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    # BFS 2-colouring; a conflict means the graph is not bipartite.
    color = {}
    for start in verts:
        if start in color:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for w in adj[u]:
                if w not in color:
                    color[w] = 1 - color[u]
                    queue.append(w)
                elif color[w] == color[u]:
                    return {"bipartite": False, "A": set(), "B": set(),
                            "n_vertices": len(verts), "n_edges": len(edges)}
    a_set = {key_to_pt[v] for v, c in color.items() if c == 0}
    b_set = {key_to_pt[v] for v, c in color.items() if c == 1}
    return {"bipartite": True, "A": a_set, "B": b_set,
            "n_vertices": len(verts), "n_edges": len(edges)}


def tile_perimeter(shape, area=1.0):
    """Perimeter of a regular tile of the given area (default 1).

    Hexagon: 6*sqrt(2*area/(3*sqrt(3))) -- least of the three.
    Square: 4*sqrt(area). Equilateral triangle:
    3*sqrt(4*area/sqrt(3)) -- most of the three. Hales (1999):
    the regular hexagon is the most efficient tiling.
    """
    if area <= 0:
        raise ValueError("area must be positive")
    if shape == "hexagon":
        return 6.0 * math.sqrt(2.0 * area / (3.0 * math.sqrt(3.0)))
    if shape == "square":
        return 4.0 * math.sqrt(area)
    if shape in ("triangle", "equilateral_triangle"):
        return 3.0 * math.sqrt(4.0 * area / math.sqrt(3.0))
    raise ValueError(f"unknown tile shape: {shape!r}")


# ---------------------------------------------------------------------------
# 3. Shipman projection (the bee link -- geometry only, see docstring)
# ---------------------------------------------------------------------------

def shipman_transition_alpha():
    """1/sqrt(3) = 0.5774: the alpha at which the arms hit the vertices.

    theta = arccot(alpha); at alpha = 1/sqrt(3), theta = 60 degrees,
    and the two arms point exactly at the hexagon vertices (the ones
    at +/-60 degrees from the top vertex). Below this alpha the curve
    family has passed the vertex direction: the topology has changed,
    analogous to the waggle-to-circle dance transition.
    """
    return 1.0 / math.sqrt(3.0)


def _hexagon_vertices_unit():
    """The 6 vertices of the unit hexagon, pointy-top (vertex at top)."""
    return [(math.sin(math.radians(60 * k)), math.cos(math.radians(60 * k)))
            for k in range(6)]


def _ray_hex_endpoint(theta):
    """Endpoint of a ray from the origin at angle theta from vertical.

    Returns (endpoint (x, y), distance, edge index) where the ray
    meets the unit hexagon boundary. theta is measured from the
    upward vertical, positive to the right.
    """
    d = (math.sin(theta), math.cos(theta))
    verts = _hexagon_vertices_unit()
    best = None
    for i in range(6):
        a = verts[i]
        b = verts[(i + 1) % 6]
        ex, ey = b[0] - a[0], b[1] - a[1]
        mat = np.array([[d[0], -ex], [d[1], -ey]], dtype=float)
        if abs(np.linalg.det(mat)) < 1e-12:
            continue
        t, s = np.linalg.solve(mat, np.array(a, dtype=float))
        if t > 1e-12 and -1e-9 <= s <= 1.0 + 1e-9:
            if best is None or t < best[0]:
                best = (t, (t * d[0], t * d[1]), i)
    if best is None:
        raise ArithmeticError("ray does not meet the hexagon")
    return best


def shipman_alpha_curve(alpha, n_samples=25):
    """The Shipman alpha curve family on the hexagon.

    Two arms from the centre at angle theta from the vertical, with
    alpha = cot(theta). Returns a dict with alpha, theta (radians and
    degrees), the two arm endpoints on the hexagon boundary, whether
    the arms have reached the vertices (theta >= 60 degrees), and a
    sampled curve (points along both arms, centre to endpoint).

    This measures the PROJECTION GEOMETRY. It does not claim the bee
    sees 6D space or that the dance is a quantum projection; see the
    module docstring for the honest framing.
    """
    if alpha <= 0:
        raise ValueError("alpha must be positive")
    theta = math.atan2(1.0, alpha)  # theta = arccot(alpha)
    _, right_end, _ = _ray_hex_endpoint(theta)
    _, left_end, _ = _ray_hex_endpoint(-theta)
    at_vertices = theta >= math.radians(60.0) - 1e-12
    curve = []
    for f in [i / (n_samples - 1) for i in range(n_samples)]:
        curve.append((f * left_end[0], f * left_end[1]))
    for f in [i / (n_samples - 1) for i in range(n_samples)]:
        curve.append((f * right_end[0], f * right_end[1]))
    return {
        "alpha": alpha,
        "theta_rad": theta,
        "theta_deg": math.degrees(theta),
        "left_endpoint": left_end,
        "right_endpoint": right_end,
        "at_vertices": at_vertices,
        "curve": curve,
    }


def shipman_arms_at_vertices(alpha):
    """True iff the arms have reached the hexagon vertices.

    theta = arccot(alpha); the arms reach the vertices at theta = 60
    degrees, i.e. alpha <= 1/sqrt(3). For alpha > 1/sqrt(3) the arms
    hit the hexagon edges between vertices (they stay inside the
    vertex-to-vertex span); for alpha < 1/sqrt(3) they have passed
    the vertex direction and the curve family has changed topology.
    """
    if alpha <= 0:
        raise ValueError("alpha must be positive")
    return math.atan2(1.0, alpha) >= math.radians(60.0) - 1e-12


# ---------------------------------------------------------------------------
# 4. Radical-pair mechanism (bee magnetoreception toy)
# ---------------------------------------------------------------------------

RPM_GAMMA = 1.76085963e11  # electron gyromagnetic ratio, rad/s/T
RPM_K = 1.0e6  # recombination rate, /s
RPM_HYPERFINE_1MT = 1.76e8  # 1 mT hyperfine coupling, rad/s

_PAULI_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
_PAULI_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
_PAULI_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
_I2 = np.eye(2, dtype=complex)


def _kron3(a, b, c):
    return np.kron(np.kron(a, b), c)


# Spin operators on (electron 1, electron 2, nucleus), each spin-1/2.
_S1 = [_kron3(s / 2.0, _I2, _I2) for s in (_PAULI_X, _PAULI_Y, _PAULI_Z)]
_S2 = [_kron3(_I2, s / 2.0, _I2) for s in (_PAULI_X, _PAULI_Y, _PAULI_Z)]
_IN = [_kron3(_I2, _I2, s / 2.0) for s in (_PAULI_X, _PAULI_Y, _PAULI_Z)]

# Electron singlet |S> = (|up,down> - |down,up>)/sqrt(2), projector on
# the electrons, identity on the nucleus. Initial state: singlet with
# a maximally mixed nucleus.
_S_VEC = np.array([0.0, 1.0 / math.sqrt(2.0), -1.0 / math.sqrt(2.0), 0.0],
                  dtype=complex)
_PS4 = np.outer(_S_VEC, _S_VEC.conj())
_RPM_PS = np.kron(_PS4, _I2)
_RPM_RHO0 = np.kron(_PS4, _I2 / 2.0)


def rpm_singlet_yield(B_vec_T, Ax, Ay, Az, k=RPM_K):
    """Singlet yield Phi_S for a field B (Tesla) and hyperfine (rad/s).

    H = gamma*(B.S1 + B.S2) + Ax*S1x*Ix + Ay*S1y*Iy + Az*S1z*Iz.
    Phi_S = k * int_0^inf P_S(t) exp(-k t) dt, computed by exact
    diagonalisation: Phi = sum_{m,n} C[m,n] * k/(k + i*(E_m - E_n)),
    real part, where C[m,n] = <m|P_S|n><n|rho(0)|m> in the energy
    eigenbasis. The Hilbert space is 8-dimensional (2 electrons +
    1 nucleus, all spin-1/2).

    This is a TOY model (one nucleus, simplified hyperfine). It
    demonstrates the compass principle; it is NOT a measurement of
    a real bee's cryptochrome.
    """
    Bx, By, Bz = (float(B_vec_T[0]), float(B_vec_T[1]), float(B_vec_T[2]))
    h = RPM_GAMMA * (Bx * _S1[0] + By * _S1[1] + Bz * _S1[2]
                     + Bx * _S2[0] + By * _S2[1] + Bz * _S2[2])
    h = h + Ax * (_S1[0] @ _IN[0]) + Ay * (_S1[1] @ _IN[1]) + Az * (_S1[2] @ _IN[2])
    energies, vecs = np.linalg.eigh(h)
    a_mat = vecs.conj().T @ _RPM_PS @ vecs
    b_mat = vecs.conj().T @ _RPM_RHO0 @ vecs
    c_mat = a_mat * b_mat.T
    d_e = energies[:, None] - energies[None, :]
    kernel = k / (k + 1.0j * d_e)
    return float(np.sum(c_mat * kernel).real)


def rpm_isotropic_yield(B_T):
    """Singlet yield for isotropic hyperfine (Ax=Ay=Az=1 mT).

    B_T is the field magnitude in Tesla (direction does not matter:
    the isotropic model has NO direction dependence -- that is its
    honest limitation, and why the anisotropic version exists).
    Measured: B=0 -> 0.6250; 25 uT -> 0.4179; 50 uT -> 0.3876;
    100 uT -> 0.3795.
    """
    a = RPM_HYPERFINE_1MT
    return rpm_singlet_yield((0.0, 0.0, float(B_T)), a, a, a)


def rpm_anisotropic_yield(B_vec_T):
    """Singlet yield for anisotropic hyperfine (Ax=Ay=0.5 mT, Az=2 mT).

    B_vec_T is the field vector in Tesla. The yield DEPENDS on the
    field direction -- that is the compass signal. Measured at
    50 uT: along z -> 0.3763; along x -> 0.2524; at 45 degrees
    (x+z) -> 0.3135; B=0 -> 0.3750.
    """
    return rpm_singlet_yield(B_vec_T, 0.5 * RPM_HYPERFINE_1MT,
                             0.5 * RPM_HYPERFINE_1MT, 2.0 * RPM_HYPERFINE_1MT)
