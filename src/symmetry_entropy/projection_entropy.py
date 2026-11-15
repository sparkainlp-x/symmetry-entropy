"""Projection entropy: what a projection knows, and what it is blind to.

Vendored from sparkainlp-x/quantum-projection v0.1.0
(quantum_projection/qsim.py and quantum_projection/membrane.py).
Provenance (carried from that repo's README): the projection code
derives from a package received under Mun Seok Lee's name. That
package is not kept here; the main code is derived from it. Mun Seok
Lee is not an author of this release, and he has not reviewed or
endorsed this software. This is an acknowledgement only: it implies
no endorsement of this code or its conclusions.

New in this package: born_weights(), projection_entropy(), and
is_kernel(). The vendored membrane is unchanged in behaviour.

Definitions
-----------
The membrane stores amplitude-encoded statevectors and projects a
probe onto the stored subspace. project() returns the complex overlaps
m_mu = <p^mu|probe>, the normalized Born weights |m_mu|^2 / sum |m|^2,
and the arg-max pattern.

projection_entropy(membrane, probe) is the Shannon entropy of the Born
weights, in bits (log2). It is the uncertainty of the projected
answer: 0 bits for a clean stored pattern (the projection is certain),
near log2(n) bits for a random probe (the projection is maximally
uncertain over n stored patterns).

is_kernel(membrane, probe) is True iff every overlap is 0: the probe
is orthogonal to every stored pattern, so all Born weights are 0 and
the projection cannot see it at all. That is the projection's blind
spot -- the kernel of the stored subspace. Note the asymmetry with the
0-bit entropy of a clean stored pattern: there 0 bits means "certain";
here the weights are all 0, which means "no answer", not "a certain
answer". projection_entropy() returns 0.0 in the kernel case because
there is no weight at all, and the docstring says so.
"""

import cmath
import math
import random

# ---------------------------------------------------------------------------
# Statevector scratchpad (vendored from qsim.py, verbatim)
# ---------------------------------------------------------------------------

SQRT1_2 = 1.0 / math.sqrt(2.0)

H = ((SQRT1_2, SQRT1_2), (SQRT1_2, -SQRT1_2))
X = ((0.0, 1.0), (1.0, 0.0))
Z = ((1.0, 0.0), (0.0, -1.0))


def _num_qubits(state):
    size = len(state)
    if size < 1 or size & (size - 1):
        raise ValueError(f"state length must be a power of two, got {size}")
    return size.bit_length() - 1


def _check_qubit(state, q):
    n = _num_qubits(state)
    if not isinstance(q, int) or isinstance(q, bool) or not 0 <= q < n:
        raise ValueError(f"qubit index {q!r} out of range for {n} qubits")


def norm(v):
    return math.sqrt(sum(abs(c) ** 2 for c in v))


def normalize(v):
    """Return v / ||v||. Raises ValueError for empty, zero or non-finite input."""
    v = [complex(c) for c in v]
    if not v:
        raise ValueError("cannot normalize an empty vector")
    if not all(cmath.isfinite(c) for c in v):
        raise ValueError("vector has non-finite entries")
    nrm = norm(v)
    if nrm == 0.0:
        raise ValueError("cannot normalize a zero-norm vector")
    return [c / nrm for c in v]


def inner(a, b):
    """<a|b> (conjugate-linear in a)."""
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} vs {len(b)}")
    return sum(x.conjugate() * y for x, y in zip(a, b))


def fidelity(a, b):
    """|<a|b>|^2 for normalized statevectors."""
    return abs(inner(a, b)) ** 2


def basis(n, index=0):
    if n < 1 or not 0 <= index < (1 << n):
        raise ValueError("bad basis state")
    s = [0j] * (1 << n)
    s[index] = 1.0 + 0j
    return s


def zero(n):
    return basis(n, 0)


def apply_1q(state, target, mat):
    """Apply a 2x2 matrix to qubit `target` (0 = least-significant)."""
    _check_qubit(state, target)
    out = [0j] * len(state)
    step = 1 << target
    for i in range(len(state)):
        if not i & step:
            a, b = i, i | step
            sa, sb = state[a], state[b]
            out[a] = mat[0][0] * sa + mat[0][1] * sb
            out[b] = mat[1][0] * sa + mat[1][1] * sb
    return out


def apply_cnot(state, control, target):
    _check_qubit(state, control)
    _check_qubit(state, target)
    if control == target:
        raise ValueError("control and target must differ")
    out = list(state)
    for i in range(len(state)):
        if (i >> control) & 1 and not (i >> target) & 1:
            j = i | (1 << target)
            out[i], out[j] = state[j], state[i]
    return out


def bell_phi_plus():
    return apply_cnot(apply_1q(zero(2), 0, H), 0, 1)


def bell_phi_minus():
    return apply_1q(bell_phi_plus(), 1, Z)


def bell_psi_plus():
    return apply_1q(bell_phi_plus(), 1, X)


def bell_psi_minus():
    return apply_1q(bell_psi_plus(), 1, Z)


def ghz(n=3):
    s = apply_1q(zero(n), 0, H)
    for c in range(n - 1):
        s = apply_cnot(s, c, c + 1)
    return s


def w_state(n=3):
    s = [0j] * (1 << n)
    for q in range(n):
        s[1 << q] = 1.0 / math.sqrt(n)
    return s


def plus_product(n):
    s = zero(n)
    for q in range(n):
        s = apply_1q(s, q, H)
    return s


def noisy(state, sigma, seed):
    """Add i.i.d. complex Gaussian noise (std sigma per real part) and renormalize."""
    if sigma < 0:
        raise ValueError("sigma must be >= 0")
    rng = random.Random(seed)
    return normalize([c + complex(rng.gauss(0, sigma), rng.gauss(0, sigma))
                      for c in state])


def random_state(n, seed):
    """Haar-random n-qubit state (normalized complex Gaussian vector)."""
    rng = random.Random(seed)
    return normalize([complex(rng.gauss(0, 1), rng.gauss(0, 1))
                      for _ in range(1 << n)])


# ---------------------------------------------------------------------------
# Projection membrane (vendored from membrane.py; KetBraPair and
# coarse_grain omitted -- not needed for the entropy functions)
# ---------------------------------------------------------------------------

def overlap(field, pattern):
    """<pattern|field>."""
    return inner(pattern, field)


def _weights(ms):
    tot = sum(abs(m) ** 2 for m in ms)
    if tot == 0.0:
        return [0.0] * len(ms)
    return [abs(m) ** 2 / tot for m in ms]


def _argmax_abs(ms):
    return max(range(len(ms)), key=lambda i: abs(ms[i]))


def _check_patterns(patterns):
    patterns = list(patterns)
    if not patterns:
        raise ValueError("need at least one pattern")
    out = [normalize(p) for p in patterns]
    dim = len(out[0])
    if any(len(p) != dim for p in out):
        raise ValueError("all patterns must have the same length")
    return out


class HolographicMembrane:
    def __init__(self, patterns):
        self.patterns = _check_patterns(patterns)
        self.dim = len(self.patterns[0])

    def _check_field(self, field):
        if len(field) != self.dim:
            raise ValueError(f"field length {len(field)} != pattern length {self.dim}")
        return normalize(field)

    def overlaps(self, field):
        field = self._check_field(field)
        return [overlap(field, p) for p in self.patterns]

    def project(self, field):
        """Overlaps, normalized weights and the arg-max pattern."""
        ms = self.overlaps(field)
        return {"overlaps": ms, "probs": _weights(ms), "winner": _argmax_abs(ms)}

    def apply_w(self, a):
        """W a = sum_mu p^mu <p^mu|a> (not normalized)."""
        out = [0j] * self.dim
        for p in self.patterns:
            m = overlap(a, p)
            for j in range(self.dim):
                out[j] += p[j] * m
        return out

    def recall(self, field, steps=1):
        """Iterate a <- W a / ||W a||. Returns (final, winner, trajectory).

        Raises ValueError if the field is orthogonal to every pattern.
        """
        if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
            raise ValueError("steps must be a positive integer")
        a = self._check_field(field)
        traj = []
        for _ in range(steps):
            a = normalize(self.apply_w(a))
            traj.append(_argmax_abs([overlap(a, p) for p in self.patterns]))
        return a, traj[-1], traj


# ---------------------------------------------------------------------------
# Projection entropy (new in this package)
# ---------------------------------------------------------------------------

_KERNEL_TOL = 1e-12


def born_weights(membrane, probe):
    """Normalized Born weights |m_mu|^2 / sum |m|^2 for the probe.

    Returns a list of floats summing to 1, or all zeros when the probe
    is orthogonal to every stored pattern (the kernel case).
    """
    return membrane.project(probe)["probs"]


def projection_entropy(membrane, probe):
    """Shannon entropy of the Born weights, in bits (log2).

    0 bits for a clean stored pattern: the projection is certain.
    Near log2(n) bits for a random probe over n stored patterns: the
    projection is maximally uncertain. 0.0 is also returned in the
    kernel case (all weights 0) -- there it means "no weight at all",
    i.e. the projection has no answer, not that it is certain.
    """
    probs = born_weights(membrane, probe)
    # + 0.0 normalizes a -0.0 result to 0.0 for clean output.
    return -sum(p * math.log2(p) for p in probs if p > 0.0) + 0.0


def is_kernel(membrane, probe):
    """True iff the probe is orthogonal to every stored pattern.

    Then every overlap is 0 (within 1e-12), every Born weight is 0,
    and the projection cannot see the probe at all: it is invisible
    to the projection. This is the kernel of the stored subspace.
    """
    return all(abs(m) < _KERNEL_TOL for m in membrane.overlaps(probe))
