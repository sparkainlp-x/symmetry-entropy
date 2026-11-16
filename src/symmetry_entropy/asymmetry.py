# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)

"""Asymmetry cost: the entropy a projection onto the symmetric part adds.

New in this package (NumPy only). No vendored code here.

Definitions
-----------
For a density matrix rho, the von Neumann entropy in bits is
S(rho) = -Tr[rho log2 rho], computed from the eigenvalues.

For a finite group G of unitaries, the twirl (group average) is
    twirl(rho) = (1/|G|) * sum_{U in G} U rho U^dagger.
The twirl is a projection onto the symmetric part: it erases exactly
the information that distinguishes the group orbit elements, and it is
idempotent (twirling twice changes nothing).

The asymmetry cost is
    cost(rho, G) = S(twirl(rho)) - S(rho) >= 0.
It is the entropy the projection onto the symmetric part adds -- the
information the projection destroys. It equals log2(|orbit|) when the
orbit elements are orthogonal and equally weighted: the cost is the
orbit entropy of the state under the group.

Concrete group used here: the Pauli group {I, X} on 1 qubit.
- |0>: orbit {|0>, |1>}, size 2. Twirl = I/2, S = 1 bit, cost = 1 bit
  = log2(2). This mirrors an asymmetric pattern (orbit 8, 3 bits):
  the state is moved by the group, so symmetrizing it costs entropy.
- |+>: X|+> = |+>, orbit size 1. Twirl = |+><+|, S = 0, cost = 0 bits
  = log2(1). This mirrors ring (orbit 1, 0 bits): the state is already
  symmetric, so symmetrizing it costs nothing -- there is nothing to
  distinguish and nothing to destroy.
"""

import math

import numpy as np

PAULI_I = np.eye(2, dtype=complex)
PAULI_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
PAULI_GROUP_IX = (PAULI_I, PAULI_X)


def ket_to_dm(psi):
    """Density matrix |psi><psi| for a 1-qubit statevector (list/array)."""
    v = np.asarray(psi, dtype=complex).reshape(-1)
    if v.shape[0] != 2:
        raise ValueError("ket_to_dm expects a 1-qubit statevector of length 2")
    nrm = np.linalg.norm(v)
    if nrm == 0.0:
        raise ValueError("cannot build a density matrix from a zero vector")
    v = v / nrm
    return np.outer(v, v.conj())


KET_ZERO = np.array([1.0, 0.0], dtype=complex)
KET_ONE = np.array([0.0, 1.0], dtype=complex)
KET_PLUS = np.array([1.0, 1.0], dtype=complex) / math.sqrt(2.0)


def von_neumann_entropy(rho):
    """Von Neumann entropy S(rho) = -Tr[rho log2 rho], in bits.

    rho must be a Hermitian density matrix with trace 1 (within 1e-9).
    Zero eigenvalues contribute 0 (0 * log 0 is taken as 0).
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("rho must be a square matrix")
    if not np.allclose(rho, rho.conj().T, atol=1e-9):
        raise ValueError("rho must be Hermitian")
    tr = float(np.trace(rho).real)
    if abs(tr - 1.0) > 1e-9:
        raise ValueError(f"rho must have trace 1, got {tr}")
    eig = np.linalg.eigvalsh(rho)
    eig = np.clip(eig, 0.0, None)
    total = float(eig.sum())
    if total <= 0.0:
        raise ValueError("rho has no positive eigenvalue")
    eig = eig / total
    # + 0.0 normalizes a -0.0 result to 0.0 for clean output.
    return float(-sum(p * math.log2(p) for p in eig if p > 0.0) + 0.0)


def twirl(rho, unitaries):
    """Group average (1/|G|) * sum_U U rho U^dagger.

    The twirl projects onto the symmetric part: it erases the
    information that distinguishes orbit elements. It is idempotent.
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError("rho must be a square matrix")
    us = [np.asarray(u, dtype=complex) for u in unitaries]
    if not us:
        raise ValueError("need at least one unitary")
    d = rho.shape[0]
    for u in us:
        if u.shape != (d, d):
            raise ValueError("every unitary must match rho's dimension")
    acc = np.zeros_like(rho)
    for u in us:
        acc = acc + u @ rho @ u.conj().T
    return acc / len(us)


def asymmetry_cost(rho, unitaries):
    """S(twirl(rho)) - S(rho), in bits. Always >= 0 (up to 1e-12 noise).

    The entropy the projection onto the symmetric part adds. It equals
    log2(|orbit|) when the orbit elements are orthogonal: the cost is
    the orbit entropy of the state under the group.
    """
    s_before = von_neumann_entropy(rho)
    s_after = von_neumann_entropy(twirl(rho, unitaries))
    cost = s_after - s_before
    if cost < -1e-12:
        raise ArithmeticError(f"asymmetry cost is negative: {cost}")
    return float(max(cost, 0.0))


def state_orbit_size(psi, unitaries):
    """Number of distinct states U|psi> under the group, up to global phase.

    Two states count as the same when their fidelity is 1 (within
    1e-9). This is the orbit size whose log2 is the asymmetry cost for
    orthogonal orbits.
    """
    v = np.asarray(psi, dtype=complex).reshape(-1)
    v = v / np.linalg.norm(v)
    seen = []
    for u in unitaries:
        w = np.asarray(u, dtype=complex) @ v
        if not any(abs(abs(np.vdot(s, w)) - 1.0) < 1e-9 for s in seen):
            seen.append(w)
    return len(seen)
