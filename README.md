# Symmetry Entropy — v0.1.0

**Symmetry entropy measures what a projection can resolve, what it must store, and what it is blind to.**

A standard-library Python plus NumPy package, in the format of
symmetry-quantum-flip-membrane and quantum-projection: deterministic
seeds, pytest, no headline claim emitted.

## What it is

Five measured quantity families, one per module:

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
5. **Honeycomb / bee-hexagon** (`honeycomb.py`) — D6 orbit entropy
   on 6-tuples (fully asymmetric hexagonal pattern: 3.585 bits;
   honeycomb cell: 0 bits); the honeycomb lattice (a patch of 7
   hexagons is bipartite, 24 vertices, 30 edges, two triangular
   sublattices 12/12) and Hales efficiency (hexagon perimeter 3.7224
   < square 4.0000 < triangle 4.5590 for unit area); the Shipman
   projection (a 6D flag manifold projects to a 2D hexagon, with an
   alpha-parameter curve family changing topology at alpha =
   1/sqrt(3) = 0.5774); and the radical-pair compass toy (singlet
   yield depends on field strength and direction: 0.3763 along z vs
   0.2524 along x at 50 uT).

`unified.py` runs eight falsifiable statements and returns measured
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
- **(e)** D6 orbit entropy bounds distinguishability: a fully
  asymmetric hexagonal pattern has 12 distinct recalls = orbit size
  12 (3.585 bits); the honeycomb cell has 1 = 1 (0.000 bits).
- **(f)** Honeycomb optimality: the hexagon has the least perimeter
  for unit area AND the honeycomb patch is bipartite (two triangular
  sublattices A and B).
- **(g)** Quantum compass: the radical-pair singlet yield is
  magnetic-field-dependent — strength AND direction (0.3763 along z
  vs 0.2524 along x at 50 uT).
- **(h)** Shipman alpha transition: the curve family changes topology
  at alpha = 1/sqrt(3) = 0.5774 (arms reach the hexagon vertices at
  theta = 60 degrees).

All eight pass. See `REPORT.md` for the measured tables.

## Install and run

```sh
pip install -e .
python -m pytest tests/          # 64 tests
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
- Shipman is a documented correlation with an unproven mechanism:
  the module measures the projection geometry, not the bee's brain.
  The radical-pair model is a one-nucleus toy, not a measurement of
  a real bee's cryptochrome.

## Licence and credits

AGPL-3.0-only. Project author: Jean-François Brisson only.

Provenance: the D4 symmetry and classical membrane code is vendored
from symmetry-quantum-flip-membrane (Brisson; Mun Seok Lee is
inspiration only there). The projection code is vendored from
quantum-projection, which derives from a package received under Mun
Seok Lee's name (see that repo's README Provenance section) —
acknowledgement only, no endorsement. Lee is not an author of this
release and has not reviewed or endorsed it.
