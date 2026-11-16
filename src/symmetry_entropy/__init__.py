# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

"""Symmetry entropy: what a projection can resolve, what it must store,
and what it is blind to.

SYNTHETIC classical emulation only. No claim about physical reality.
No headline claim is emitted (see unified.unified_claim()).

Import the functions from their modules, e.g.::

    from symmetry_entropy.orbit import orbit, orbit_entropy
    from symmetry_entropy.projection_entropy import projection_entropy
    from symmetry_entropy.asymmetry import asymmetry_cost
    from symmetry_entropy.self_determinism import self_determinism_factor
    from symmetry_entropy.honeycomb import d6_orbit_entropy, rpm_anisotropic_yield
    from symmetry_entropy.unified import unified_claim
"""

from . import asymmetry, honeycomb, orbit, projection_entropy, self_determinism, unified

__version__ = "0.1.0"

__all__ = ["asymmetry", "honeycomb", "orbit", "projection_entropy", "self_determinism", "unified"]
