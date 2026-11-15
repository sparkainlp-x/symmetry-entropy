"""Self-determinism factor: how much of a projection the system determines itself.

New in this package (upgrade, v0.1.0). This is the fourth quantity,
alongside orbit entropy, projection entropy, and asymmetry cost.

Definition (quantum membrane)
------------------------------
For a probe |psi> and stored patterns {|p^mu>}, the self-determinism
factor is

    D(psi) = <psi|P|psi> = ||P|psi>||^2,

where P is the orthogonal projector onto the stored subspace
span{p^mu}. D is in [0, 1]:

- D = 1: the probe lies entirely in the stored subspace. The outcome
  is fully determined by the system's own memory -- the probe only
  selects among stored patterns. The projection is fully
  self-determined.
- D = 0: the probe is orthogonal to every stored pattern (the kernel).
  The system determines nothing -- it is blind. This is claim (b).
- 0 < D < 1: partially self-determined. The probe has a component in
  the stored subspace (which the projection can resolve) and a
  component in the kernel (which it cannot).

For orthonormal stored patterns (the Bell-state membrane in this
package), P = sum_mu |p^mu><p^mu| and D reduces to sum_mu
|<p^mu|psi>|^2 -- the total Born weight before normalisation. That is
the key relationship to projection entropy: the Born weights are
w_mu = |m_mu|^2 / D, and the projection entropy is the Shannon
entropy of those normalised weights. So D says HOW MUCH the system
can see at all, and the projection entropy says how UNCERTAIN the
answer is given what it can see. They are complementary: D is the
denominator of the Born weights.

Definition (classical membrane)
--------------------------------
For a classical 16-cell probe, the self-determinism factor is

    D(probe) = max_mu |overlap(probe, p^mu)|^2,

the best squared normalised overlap with any stored pattern. D = 1
means the probe IS a stored pattern (fully self-determined); D = 0
means it is orthogonal to every stored pattern. In closed-orbit mode
every transform of a stored pattern has D = 1. In base-only mode a
transformed probe has D < 1: the missing part is exactly the orbit
information base-only mode never stored. For alpha rot90 in base-only
mode, D = 0.25 -- the transform's best overlap with a base pattern is
0.5, squared.

What D is and is not
--------------------
D is a property of a probe relative to a stored subspace. It measures
how much of an outcome the system's own structure determines, versus
how much comes from outside it (the probe's component in the kernel).
It does NOT measure consciousness, free will, or anything about
physical reality: this is synthetic classical code, the stored
subspace is built by the programmer, and D is a number computed from
that construction. The honest limit from REPORT.md applies here too.
"""

import math

import numpy as np


def _projector_basis(patterns):
    """Orthonormal basis (columns of Q) for span{patterns}, via QR.

    patterns is a list of statevectors (lists of complex numbers).
    Returns Q as a numpy array of shape (dim, rank). For orthonormal
    patterns Q is the patterns themselves.
    """
    mat = np.array([[complex(c) for c in p] for p in patterns],
                   dtype=complex).T
    q, _ = np.linalg.qr(mat)
    # QR of a rank-deficient matrix still returns a valid orthonormal
    # basis for the column space (with extra orthonormal columns); the
    # projector below uses only the first `rank` columns.
    rank = int(np.linalg.matrix_rank(mat))
    return q[:, :rank]


def self_determinism_factor(membrane, probe):
    """D = <probe|P|probe> for the quantum membrane, in [0, 1].

    P is the orthogonal projector onto the stored subspace. Computed
    from an orthonormal basis of span{patterns}; for orthonormal
    stored patterns this equals sum_mu |<p^mu|probe>|^2, the total
    Born weight before normalisation.
    """
    patterns = membrane.patterns
    psi = np.array([complex(c) for c in membrane._check_field(probe)],
                   dtype=complex)
    q = _projector_basis(patterns)
    projected = q.conj().T @ psi
    return float(np.sum(np.abs(projected) ** 2))


def classical_self_determinism(membrane, probe):
    """D = max_mu |overlap(probe, p^mu)|^2 for the classical membrane.

    The best squared normalised overlap with any stored pattern.
    D = 1 means the probe is a stored pattern; D = 0 means it is
    orthogonal to every stored pattern.
    """
    overlaps = membrane.overlaps(probe)
    values = overlaps.values() if isinstance(overlaps, dict) else overlaps
    return max(abs(v) ** 2 for v in values)


def self_determinism_gap(membrane, probe):
    """1 - D: the fraction of the probe the projection cannot determine.

    0 means fully self-determined; 1 means entirely in the kernel
    (invisible). This is the complement of self_determinism_factor.
    """
    return 1.0 - self_determinism_factor(membrane, probe)
