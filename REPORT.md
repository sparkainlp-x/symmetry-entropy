# Symmetry Entropy — REPORT v0.1.0

## Summary

Symmetry entropy measures what a projection can resolve, what it must
store, and what it is blind to. Five measured quantity families,
eight falsifiable claims, all measured on the real vendored code. No
headline claim is emitted (`headline_allowed` is always False).

## 1. Orbit entropy (D4 on 4x4 ±1 patterns)

`orbit_entropy(pattern) = log2(|orbit|)`, the information the
projection must resolve to tell the orbit elements apart.

| pattern | orbit size | orbit entropy (bits) | distinct recalls (closed-orbit) |
|---|---|---|---|
| alpha | 8 | 3.000 | 8 |
| beta | 8 | 3.000 | 8 |
| gamma | 8 | 3.000 | 8 |
| delta | 8 | 3.000 | 8 |
| blocks | 2 | 1.000 | 2 |
| ring | 1 | 0.000 | 1 |
| cross | 1 | 0.000 | 1 |

Closed-orbit storage of the 4 asymmetric bases: **32 distinct
patterns**. The combined membrane (all 7 patterns' closed orbits)
holds 36 distinct stored patterns.

### Negative result kept: base-only equivariance fails

Recalling the 7 non-identity D4 transforms of each base pattern
against the base-only membrane (4 patterns) returns the wrong base
most of the time. Correct counts, measured:

| base | correct / 7 | mis-recalled as |
|---|---|---|
| alpha | 3 | rot90→beta, rot270→beta, transpose→delta, anti_transpose→delta |
| beta | 2 | — |
| gamma | 3 | — |
| delta | 4 | — |
| **total** | **12 / 28** | **16 wrong** |

The projection cannot resolve the orbit because the orbit was never
stored. The orbit entropy (3 bits) is exactly the information
base-only mode lacks. The falsified symmetric design (blocks, ring,
cross) is the same mechanism from the other side: ring at 0 bits
cannot be distinguished from any of its transforms, because there
are no distinct transforms.

## 2. Projection entropy (stored Φ+, Φ−, Ψ+; max log2 3 = 1.585 bits)

`projection_entropy` is the Shannon entropy of the Born weights
`|m|²/Σ|m|²` after projecting onto the stored subspace.

| probe | weights | projection entropy (bits) |
|---|---|---|
| Φ+ clean | [1.000, 0.000, 0.000] | 0.000 |
| Φ+ noisy σ=0.25, seed 11 | [0.872, 0.113, 0.015] | 0.618 |
| Φ+ noisy σ=0.75, seed 11 | [0.474, 0.465, 0.061] | 1.270 |
| Haar-random 2-qubit, seed 7 | [0.315, 0.368, 0.317] | 1.581 |
| Haar-random 2-qubit, seed 42 | [0.199, 0.204, 0.597] | 1.375 |
| Ψ− clean | [0.000, 0.000, 0.000] | 0.000 (no weight at all) |

A clean stored pattern projects with 0 bits (certain). A random
state projects with ~1.58 bits (near-maximal uncertainty over 3
patterns). The projection creates the uncertainty: a definite input
state becomes a distribution over patterns.

### Negative result kept: the kernel is invisible

Ψ− is orthogonal to every stored pattern, so every overlap is 0,
every Born weight is 0, and `is_kernel` is True. The projection has
no answer for it — not a wrong answer, no answer. This is the kernel
of the stored subspace: the part of the space the projection cannot
see. Note the asymmetry with the 0-bit entropy of a clean stored
pattern: there 0 bits means "certain"; here the weights are all 0,
which means "no answer".

## 3. Asymmetry cost (Pauli group {I, X} on 1 qubit)

`asymmetry_cost(ρ) = S(twirl(ρ)) − S(ρ)`, the von Neumann entropy the
projection onto the symmetric part adds. The twirl is idempotent: it
is a projection.

| state | S(ρ) (bits) | S(twirl) (bits) | cost (bits) | orbit size | log2 orbit |
|---|---|---|---|---|---|
| \|0⟩ | 0.000 | 1.000 | 1.000 | 2 | 1.000 |
| \|1⟩ | 0.000 | 1.000 | 1.000 | 2 | 1.000 |
| \|+⟩ | 0.000 | 0.000 | 0.000 | 1 | 0.000 |

|0⟩ costs 1 bit = log2(2): the state is moved by the group, so
symmetrizing it costs entropy. |+⟩ costs 0 bits = log2(1): the
state is already symmetric, so symmetrizing it costs nothing. This
mirrors ring (0 bits) vs an asymmetric pattern (3 bits).

## 4. Self-determinism factor D (new)

`D = <psi|P|psi>`, the squared norm of the probe's projection onto
the stored subspace, in [0, 1]. For orthonormal stored patterns this
is sum_mu |<p^mu|psi>|^2 -- the total Born weight BEFORE
normalisation. The Born weights are w_mu = |m_mu|^2 / D, so D is the
denominator of the weights: D says HOW MUCH the system can see at
all, and the projection entropy (§2) says how UNCERTAIN the answer is
given what it can see. They are complementary.

| probe (quantum, stored Φ+, Φ−, Ψ+) | D |
|---|---|
| Φ+ clean | 1.000 |
| Φ+ noisy σ=0.25, seed 11 | 0.843 |
| Φ+ noisy σ=0.75, seed 11 | 0.567 |
| Ψ− clean (kernel) | 0.000 |
| Haar-random 2-qubit, seed 7 | 0.910 |
| Haar-random 2-qubit, seed 42 | 0.193 |
| Haar-random 2-qubit, mean over 200 seeds | 0.720 (expected 3/4: the stored subspace is 3 of 4 dims) |

| probe (classical) | D |
|---|---|
| alpha clean (closed-orbit) | 1.000 |
| alpha rot90 (closed-orbit) | 1.000 |
| ring, any transform (closed-orbit) | 1.000 |
| alpha clean (base-only) | 1.000 |
| alpha rot90 (base-only) | 0.250 |
| alpha rot180 (base-only) | 0.250 |

D = 1 goes with projection entropy 0 (certain); D = 0 goes with the
kernel (all weights 0, no answer). In base-only mode a transformed
probe has D = 0.25: its best overlap with a base pattern is 0.5,
squared. The missing 0.75 is exactly the orbit information base-only
mode never stored -- the same lack behind the 12/28 equivariance
failure in §1.

## 5. Honeycomb / bee-hexagon extension (new)

The D4 symmetry of §1 extends to the hexagon (D6, 12 operations),
and the hexagonal geometry connects to three documented facts:
Hales' honeycomb conjecture, Shipman's flag-manifold correlation
with the honeybee waggle dance, and the radical-pair mechanism of
bee magnetoreception.

### 5a. D6 orbit entropy (6-tuples on a hexagonal ring)

`d6_orbit_entropy(pattern) = log2(|orbit|)` under D6.

| pattern | orbit size | orbit entropy (bits) | distinct recalls (closed-orbit) |
|---|---|---|---|
| asymmetric (1,1,−1,1,−1,−1) | 12 | 3.585 | 12 |
| alternating (1,−1,1,−1,1,−1) | 2 | 1.000 | 2 |
| honeycomb cell (all +1) | 1 | 0.000 | 1 |
| one −1 | 6 | 2.585 | 6 |
| two adjacent −1 | 6 | 2.585 | 6 |
| two opposite −1 | 3 | 1.585 | 3 |

A fully asymmetric hexagonal pattern has 3.585 bits -- larger than
D4's 3.000 bits, because the hexagon has more symmetry to break (12
operations vs 8). The honeycomb cell has orbit 1 (0.000 bits), like
the D4 ring: fully symmetric, nothing to distinguish.

### 5b. Honeycomb lattice and Hales efficiency

A honeycomb patch (one central hexagon plus its 6 neighbours) is a
bipartite graph: **24 vertices, 30 edges, split 12/12 between two
triangular sublattices A and B** -- the same bipartite structure as
graphene (two interpenetrating triangular sublattices, whose symmetry
protects the Dirac cones).

For unit area, the regular hexagon has the least perimeter of the
three regular tilings (Hales, 1999):

| tile | perimeter (unit area) |
|---|---|
| hexagon | 3.7224 |
| square | 4.0000 |
| equilateral triangle | 4.5590 |

3.7224 < 4.0000 < 4.5590. The bee minimises wax; the quantum
material's honeycomb symmetry protects its Dirac points. Same shape,
same reason (optimisation), different physics.

### 5c. Shipman projection (geometry only)

Barbara Shipman (University of Rochester) found that the
6-dimensional flag manifold -- a quantum geometry used for quarks --
projects to a 2-dimensional HEXAGON, and that curves in the flag
manifold, projected onto that hexagon, reproduce the honeybee waggle
dance. A variable alpha reproduces the whole dance. The curve family
changes topology at **alpha = 1/sqrt(3) = 0.5774** (theta = 60
degrees, the arms reach the hexagon vertices):

| alpha | theta (deg) | arms |
|---|---|---|
| 2.000 | 26.57 | inside (hit the edges) |
| 1.000 | 45.00 | inside (hit the edges) |
| 0.5774 | 60.00 | AT the vertices (endpoint distance 1.000) |
| 0.400 | 68.20 | passed the vertex direction |
| 0.200 | 78.69 | passed the vertex direction |

HONEST FRAMING: Shipman's correlation is DOCUMENTED (Discover,
November 1997, Adam Frank) but the mechanism is UNPROVEN -- no
follow-up papers in 20 years, no other academics continued it, one
entomologist called it "ridiculous". What is measured here is the
PROJECTION GEOMETRY (a 6D object projecting to a 2D hexagon, and an
alpha-parameter curve family with a topology transition), NOT the
bee's brain. This module does NOT claim bees see 6D space, and it
does NOT claim the dance IS a quantum projection.

### 5d. Radical-pair mechanism (bee magnetoreception toy)

Two electron spins + one nuclear spin, H = gamma*(B.S1 + B.S2) +
(Ax*S1x*Ix + Ay*S1y*Iy + Az*S1z*Iz), gamma = 1.76085963e11 rad/s/T,
k = 1.0e6 /s, electron singlet with maximally mixed nucleus, exact
diagonalisation. Singlet yield Phi_S:

| case | field | yield |
|---|---|---|
| isotropic (Ax=Ay=Az=1 mT) | B = 0 | 0.6250 |
| isotropic | B = 25 uT | 0.4179 |
| isotropic | B = 50 uT | 0.3876 |
| isotropic | B = 100 uT | 0.3795 |
| anisotropic (Ax=Ay=0.5 mT, Az=2 mT) | B = 0 | 0.3750 |
| anisotropic | B = 50 uT along z | 0.3763 |
| anisotropic | B = 50 uT along x | 0.2524 |
| anisotropic | B = 50 uT at 45 deg (x+z) | 0.3135 |

The isotropic yield depends on field STRENGTH but NOT on direction
(B along z and along x both give 0.3876 at 50 uT) -- that is its
honest limitation, and why the anisotropic version exists. The
anisotropic yield depends on DIRECTION: **0.3763 along z vs 0.2524
along x at 50 uT, a contrast of 0.1239** -- that direction
dependence IS the compass signal, the leading mechanism for bee
magnetoreception (cryptochrome).

HONEST FRAMING: this is a TOY model (one nucleus, simplified
hyperfine). It demonstrates the compass PRINCIPLE; it is NOT a
measurement of a real bee's cryptochrome, which has many nuclei and
a complex environment. Experimental context: Oesterle et al. 2026
(two-photon imaging of the bee anterior optic tubercle).

## 6. The eight claims (measured)

**(a) Distinguishability is bounded by orbit entropy — PASS.**
In closed-orbit mode, distinct recalls equal orbit size for every
pattern: 8/8/8/8 for the asymmetric bases, 2 for blocks, 1 for ring,
1 for cross. The projection resolves exactly as much as the orbit
entropy allows — no more.

**(b) The projection's kernel is invisible — PASS.** Ψ− has all Born
weights 0 and `is_kernel` True. The projection cannot see a state
orthogonal to the stored subspace.

**(c) The projected world has higher entropy than the underlying
state by the asymmetry cost — PASS**, in both cases:
- Classical: a single definite pattern has entropy 0; the uniform
  distribution over its orbit has entropy log2(|orbit|). Gap = orbit
  entropy: alpha 3.000 bits, ring 0.000 bits.
- Quantum: S(twirl) − S(ρ) = log2(orbit size): |0⟩ 1.000 bit,
  |+⟩ 0.000 bits.

**(d) The projection is self-determined exactly to the extent the
probe lies in the stored subspace — PASS.** D = 1 for a clean stored
probe (Φ+ 1.000, projection entropy 0); D = 0 for a kernel probe
(Ψ− 0.000, all weights 0, `is_kernel` True); strictly between 0 and
1 for noisy and random probes (Φ+ σ=0.25: 0.843; σ=0.75: 0.567;
Haar seed 7: 0.910; seed 42: 0.193; mean over 200 seeds 0.720).
Classical: D = 1 for every stored transform in closed-orbit mode;
D = 0.25 for a transformed probe in base-only mode.

**(e) D6 orbit entropy bounds distinguishability — PASS.**
Fully asymmetric hexagonal pattern: 12 distinct recalls = orbit
size 12 (3.585 bits). Honeycomb cell: 1 = 1 (0.000 bits).
Alternating: 2 = 2. One −1: 6 = 6. Two opposite −1: 3 = 3.

**(f) Honeycomb optimality — PASS.** Hexagon has the least
perimeter for unit area (3.7224 < 4.0000 < 4.5590) AND the
honeycomb patch is bipartite (24 vertices, 30 edges, two triangular
sublattices A and B, 12/12).

**(g) Quantum compass — PASS.** The radical-pair singlet yield is
magnetic-field-dependent: strength (isotropic: 0.6250 at 0 uT ->
0.3876 at 50 uT) AND direction (anisotropic: 0.3763 along z vs
0.2524 along x at 50 uT, contrast 0.1239).

**(h) Shipman alpha transition — PASS.** The curve family changes
topology at alpha = 1/sqrt(3) = 0.5774 (arms reach the hexagon
vertices at theta = 60 degrees); above it the arms stay inside,
below it they have passed the vertex direction.

Overall: **8/8 claims pass. `headline_allowed` is False.**

## 7. Honest limits

1. **Classical emulation only, no claim about physical reality.**
   This package is synthetic classical code. It cannot prove anything
   about physical reality, because it does not interact with physical
   reality. A classical program that projects proves that classical
   programs can project.
2. **The projector W is an input, not a discovery.** `W = Σ|p⟩⟨p|`
   is built by the programmer. That recall converges to the dominant
   eigenvector is a theorem about that matrix, not a discovery about
   nature. Building a projector in code and watching it work cannot
   prove the mechanism exists in nature — that would be circular.
3. **Symmetry entropy is mechanism-neutral.** Orbit entropy and
   projection entropy are mathematical properties of any state with a
   symmetry group — classical or quantum, projected or not. They do
   not discriminate "reality is a projection" from "reality is
   unitary evolution with symmetries" or "reality is classical with
   symmetries". What they measure is what a projection can resolve,
   what it must store, and what it is blind to — not which mechanism
   nature uses.
4. **No Bell violation, no speedup, no hardware.** All correlations
   are classical numbers in one array; n qubits cost 2^n complex
   numbers. No headline claim is emitted. Results apply only to the
   recorded seeds, patterns, and noise levels.
5. **D is a property of a probe relative to a stored subspace built
   by the programmer.** It measures how much of an outcome the
   system's own structure determines versus how much comes from
   outside it. It does not measure consciousness, free will, or
   anything about physical reality.
6. **Shipman is a documented correlation with an unproven mechanism,
   and the RPM here is a toy.** The Shipman section measures the
   PROJECTION GEOMETRY (a 6D object projecting to a 2D hexagon, and
   an alpha-parameter curve family with a topology transition), not
   the bee's brain; it does not claim bees see 6D space or that the
   dance is a quantum projection. The RPM section is a one-nucleus
   toy with simplified hyperfine; it demonstrates the compass
   principle, not a measurement of a real bee's cryptochrome.

## 8. What would count as proof (the bar, not met here)

A falsifiable prediction that separates projection from the
alternatives, tested on a physical system — for example: a maximum
distinguishable dimension (finite memory) with systematic
misassignment beyond it; states in the orthogonal complement
systematically invisible rather than merely noisy; an entropy gap
between the projected world and the underlying state equal to the
asymmetry cost, matching the symmetry-entropy prediction and not
the alternatives. This package tests all three *in the model*.
Crossing to physical reality needs a physical measurement.
