# Changelog

## 0.1.0 — 2026-11-15

Initial release.

- `orbit.py`: D4 symmetry operations and classical holographic membrane
  vendored from symmetry-quantum-flip-membrane v0.1.0; new orbit(),
  orbit_entropy(), distinct_recalls(); falsified symmetric patterns
  (blocks, ring, cross) kept and measured.
- `projection_entropy.py`: statevector scratchpad and projection
  membrane vendored from quantum-projection v0.1.0; new born_weights(),
  projection_entropy(), is_kernel().
- `asymmetry.py`: von Neumann entropy, twirl, asymmetry cost (NumPy);
  Pauli group {I, X} on 1 qubit as the concrete group.
- `unified.py`: unified_claim() runs the eight falsifiable statements
  (distinguishability bounded by orbit entropy; kernel invisibility;
  projected entropy exceeds underlying entropy by the asymmetry cost;
  self-determined exactly to the extent the probe lies in the stored
  subspace; D6 orbit entropy bounds distinguishability; honeycomb
  optimality; quantum compass; Shipman alpha transition) and returns
  measured numbers with pass/fail each. headline_allowed is always
  False; no headline claim is emitted.
- `self_determinism.py`: self_determinism_factor() (D = <psi|P|psi>,
  the squared norm of a probe's projection onto the stored subspace),
  classical_self_determinism() (max |overlap|^2), and
  self_determinism_gap() (1 - D). D is the denominator of the Born
  weights: it says how much the system can see at all, and the
  projection entropy says how uncertain the answer is given that.
- `honeycomb.py`: D6 symmetry on 6-tuples (d6_orbit(),
  d6_orbit_entropy(), HexMembrane, d6_distinct_recalls());
  honeycomb_patch_bipartite() (7-hexagon patch: bipartite, 24
  vertices, 30 edges, sublattices 12/12) and tile_perimeter()
  (Hales: hexagon 3.7224 < square 4.0000 < triangle 4.5590);
  shipman_alpha_curve() / shipman_transition_alpha() (topology
  transition at alpha = 1/sqrt(3) = 0.5774; geometry only, mechanism
  unproven); rpm_singlet_yield() / rpm_isotropic_yield() /
  rpm_anisotropic_yield() (radical-pair compass toy by exact
  diagonalisation; direction contrast 0.3763 vs 0.2524 at 50 uT).
- `unified.py`: now runs eight falsifiable statements (a)-(h).
