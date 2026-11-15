# Symmetry Entropy — v0.1.0

**Symmetry entropy measures what a projection can resolve, what it must store, and what it is blind to.**

A standard-library Python plus NumPy package, in the format of
symmetry-quantum-flip-membrane and quantum-projection: deterministic
seeds, pytest, no headline claim emitted.

## What it is

Four measured quantities, one per module:

1. **Orbit entropy** (`orbit.py`) — `log2(|orbit|)` under the dihedral
   group D4 on 4x4 ±1 patterns. Asymmetric patterns: 3 bits. blocks:
   1 bit. ring and cross: 0 bits (the orbit has collapsed).
2. **Projection entropy** (`projection_entropy.py`) — the Shannon
   entropy of the Born weights after projecting a statevector onto a
   stored subspace. 0 bits for a clean stored Bell state, 0.618 bits
   at noise σ=0.25, 1.270 bits at σ=0.75, 1.581 bits for a Haar-random
   state (max log2 3 = 1.585 bits).
3. **Asymmetry cost** (`asymmetry.py`) — `S(twirl(ρ)) − S(ρ)`, the
   von Neumann entropy the projection onto the symmetric part adds,
   under the Pauli group {I, X} on 1 qubit. |0⟩ costs 1 bit = log2(2);
   |+⟩ costs 0 bits = log2(1).
4. **Self-determinism factor** (`self_determinism.py`) — `D =
   <psi|P|psi>`, the squared norm of a probe's projection onto the
   stored subspace, in [0, 1]. D = 1 for a clean stored probe (fully
   self-determined), D = 0 for a kernel probe (invisible), and
   strictly between for noisy and random probes. D is the denominator
   of the Born weights: it says how much the system can see at all,
   and the projection entropy says how uncertain the answer is given
   what it can see.

`unified.py` runs four falsifiable statements and returns measured
numbers with a pass/fail for each:

- **(a)** Distinguishability is bounded by orbit entropy: in
  closed-orbit mode, distinct recalls equal orbit size.
- **(b)** The projection's kernel is invisible: Ψ−, orthogonal to
  every stored pattern, has all Born weights 0.
- **(c)** The projected world has higher entropy than the underlying
  state by the asymmetry cost — in the classical orbit case AND the
  quantum twirl case.
- **(d)** The projection is self-determined exactly to the extent the
  probe lies in the stored subspace: D = 1 for a clean stored probe,
  D = 0 for a kernel probe, strictly between for noisy and random
  probes; the classical analogue holds in closed-orbit and base-only
  mode.

All four pass. See `REPORT.md` for the measured tables.

## Install and run

```sh
pip install -e .
python -m pytest tests/          # 46 tests
symmetry-entropy                 # prints the unified claim as JSON
```

## Honest limits

- Synthetic toy only. Classical emulation, no claim about physical
  reality. NOT quantum mechanics, NOT optical holography, NOT a proof
  that reality is a projection.
- The projector `W = Σ|p⟩⟨p|` is an input built by the programmer,
  not a discovery: convergence is a theorem about that matrix.
- Symmetry entropy is mechanism-neutral: it does not discriminate
  "reality is a projection" from "reality is unitary evolution with
  symmetries" or "reality is classical with symmetries".
- No speedup, no Bell violation, no hardware data.
- No headline claim is emitted: `headline_allowed` is always False.
- Results apply only to the recorded seeds, patterns, and noise levels.

## Licence and credits

AGPL-3.0-only. Project author: Jean-François Brisson only.

Provenance: the D4 symmetry and classical membrane code is vendored
from symmetry-quantum-flip-membrane (Brisson; Mun Seok Lee is
inspiration only there). The projection code is vendored from
quantum-projection, which derives from a package received under Mun
Seok Lee's name (see that repo's README Provenance section) —
acknowledgement only, no endorsement. Lee is not an author of this
release and has not reviewed or endorsed it.
