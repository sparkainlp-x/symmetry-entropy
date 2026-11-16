# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

"""Orbit entropy: what a symmetry can and cannot resolve.

Vendored from sparkainlp-x/symmetry-quantum-flip-membrane v0.1.0
(D4 symmetry operations, base patterns, and the classical holographic
membrane). Provenance: that package is by Jean-Francois Brisson only;
Mun Seok Lee is cited there as inspiration only, not as co-author,
because it contains no Digital to Wave, Coherent Sequence, C_seq, or
OES-32 code. The same holds here: Lee is not an author of this package
and has not reviewed or endorsed it.

New in this package: orbit(), orbit_entropy(), distinct_recalls(),
and the falsified symmetric patterns (blocks, ring, cross), whose
orbits collapse. The falsified design is kept and measured, not hidden:
symmetric patterns have small orbits, so a projection cannot
distinguish which base a transformed probe came from. That is the
mechanism this package measures.

Definitions
-----------
A pattern is a tuple of 16 values in {-1, +1}, in row-major order.
The dihedral group D4 (8 operations) acts on the 4x4 grid.

orbit_entropy(pattern) = log2(|orbit|) in bits, where |orbit| is the
number of *distinct* D4 transforms of the pattern. It is the
information the projection must resolve to tell the orbit elements
apart: an asymmetric pattern has orbit 8 (3 bits); a fully symmetric
pattern has orbit 1 (0 bits) and there is nothing to distinguish.
"""

import math

# ---------------------------------------------------------------------------
# D4 symmetry operations (vendored from symmetry.py, verbatim)
# ---------------------------------------------------------------------------

OPS = ("identity", "rot90", "rot180", "rot270",
       "flip_h", "flip_v", "transpose", "anti_transpose")


def _perm_for(op):
    """Return a tuple p where new[i] = old[p[i]] for grid position i."""
    perm = []
    for r in range(4):
        for c in range(4):
            if op == "identity":
                sr, sc = r, c
            elif op == "rot90":
                sr, sc = 3 - c, r
            elif op == "rot180":
                sr, sc = 3 - r, 3 - c
            elif op == "rot270":
                sr, sc = c, 3 - r
            elif op == "flip_h":
                sr, sc = r, 3 - c
            elif op == "flip_v":
                sr, sc = 3 - r, c
            elif op == "transpose":
                sr, sc = c, r
            elif op == "anti_transpose":
                sr, sc = 3 - c, 3 - r
            else:
                raise ValueError(f"unknown symmetry operation: {op!r}")
            perm.append(sr * 4 + sc)
    return tuple(perm)


PERMS = {op: _perm_for(op) for op in OPS}

INVERSE = {
    "identity": "identity", "rot90": "rot270", "rot180": "rot180",
    "rot270": "rot90", "flip_h": "flip_h", "flip_v": "flip_v",
    "transpose": "transpose", "anti_transpose": "anti_transpose",
}


def apply_op(pattern, op):
    """Apply a D4 operation to a 16-cell pattern."""
    if len(pattern) != 16:
        raise ValueError("pattern must have exactly 16 cells")
    if op not in PERMS:
        raise ValueError(f"unknown symmetry operation: {op!r}")
    perm = PERMS[op]
    return tuple(pattern[perm[i]] for i in range(16))


def inverse_op(op):
    return INVERSE[op]


# ---------------------------------------------------------------------------
# Classical holographic membrane (vendored from membrane.py, verbatim)
# ---------------------------------------------------------------------------

BASE_PATTERNS = {
    # Asymmetric patterns, chosen so each D4 orbit has 8 distinct patterns
    # and no orbit collides with another base pattern's orbit (32 distinct
    # stored patterns in closed-orbit mode). Hand-drawn symmetric patterns
    # (blocks, cross, diag, ring) were REJECTED: blocks is invariant under
    # rot180, ring under several operations, so their orbits collide and
    # recall cannot distinguish which base a transformed probe came from.
    # That collision gave closed-orbit equivariance of only 0.5, measured
    # before this change; it is kept as a falsified design in DESIGN.md.
    "alpha": (-1, -1, -1, 1, 1, 1, -1, 1, 1, 1, 1, 1, 1, -1, -1, 1),
    "beta": (1, 1, -1, -1, -1, -1, 1, -1, -1, 1, 1, 1, -1, 1, 1, -1),
    "gamma": (1, 1, 1, 1, 1, -1, -1, 1, 1, 1, 1, 1, -1, 1, -1, 1),
    "delta": (1, 1, -1, 1, -1, 1, 1, -1, -1, 1, 1, 1, -1, -1, 1, -1),
}

SEQUENCE = ("alpha", "beta", "gamma", "delta")

# Falsified symmetric hand patterns (the rejected first design, kept and
# measured here). Their orbits collapse: blocks is invariant under
# rot180 / transpose / anti_transpose (orbit 2, 1 bit); ring and cross
# are invariant under all 8 D4 operations (orbit 1, 0 bits). A projection
# cannot distinguish a pattern from its transforms when the orbit has
# only one element -- there is nothing to distinguish.
FALSIFIED_PATTERNS = {
    "blocks": (1, 1, -1, -1, 1, 1, -1, -1, -1, -1, 1, 1, -1, -1, 1, 1),
    "ring": (1, 1, 1, 1, 1, -1, -1, 1, 1, -1, -1, 1, 1, 1, 1, 1),
    "cross": (-1, 1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, 1, -1),
}


def overlap(a, b):
    if len(a) != 16 or len(b) != 16:
        raise ValueError("patterns must have exactly 16 cells")
    return sum(x * y for x, y in zip(a, b)) / 16.0


class HolographicMembrane:
    """Outer-product memory over named 16-cell patterns."""

    def __init__(self, patterns):
        self.patterns = {}
        for name, pat in patterns.items():
            if len(pat) != 16 or any(x not in (-1, 1) for x in pat):
                raise ValueError(f"pattern {name!r} must be 16 cells in {{-1, +1}}")
            self.patterns[name] = tuple(pat)
        # Outer-product matrix, kept for provenance; recall uses overlaps,
        # which are exactly the normalised projection onto stored patterns.
        self.matrix = [[0.0] * 16 for _ in range(16)]
        for pat in self.patterns.values():
            for i in range(16):
                for j in range(16):
                    self.matrix[i][j] += pat[i] * pat[j]

    def overlaps(self, probe):
        if len(probe) != 16 or any(x not in (-1, 1) for x in probe):
            raise ValueError("probe must be 16 cells in {-1, +1}")
        return {name: overlap(probe, pat) for name, pat in self.patterns.items()}

    def recall(self, probe):
        """Return (best_name, best_overlap, all_overlaps). No gate here."""
        ov = self.overlaps(probe)
        best = max(ov, key=lambda k: ov[k])
        return best, ov[best], ov


def closed_orbit_patterns():
    """All 8 D4 transforms of each base pattern, named ``base@op``.

    For the asymmetric bases every transform is distinct, so this is
    32 distinct stored patterns. (Symmetric patterns would collide:
    that is the falsified design.)
    """
    out = {}
    for name, pat in BASE_PATTERNS.items():
        for op in OPS:
            out[f"{name}@{op}"] = apply_op(pat, op)
    return out


# ---------------------------------------------------------------------------
# Orbit entropy (new in this package)
# ---------------------------------------------------------------------------

def orbit(pattern):
    """Set of distinct D4 transforms of a 16-cell pattern."""
    if len(pattern) != 16:
        raise ValueError("pattern must have exactly 16 cells")
    return {apply_op(pattern, op) for op in OPS}


def orbit_entropy(pattern):
    """log2 of the orbit size, in bits.

    The information the projection must resolve to tell the orbit
    elements apart. Asymmetric patterns: log2(8) = 3 bits. blocks:
    log2(2) = 1 bit. ring / cross: log2(1) = 0 bits -- the orbit has
    collapsed and there is nothing to distinguish.
    """
    return math.log2(len(orbit(pattern)))


def distinct_recalls(membrane, pattern):
    """Number of distinct recalls across the orbit, in closed-orbit mode.

    Each distinct transform of the pattern is recalled against the
    membrane; the return value is how many distinct stored names come
    back. In closed-orbit mode this equals the orbit size: the
    projection resolves exactly as much as the orbit entropy allows.
    """
    names = set()
    for transformed in orbit(pattern):
        name, _, _ = membrane.recall(transformed)
        names.add(name)
    return len(names)
