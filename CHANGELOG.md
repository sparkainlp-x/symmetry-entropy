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
- `unified.py`: unified_claim() runs the four falsifiable statements
  (distinguishability bounded by orbit entropy; kernel invisibility;
  projected entropy exceeds underlying entropy by the asymmetry cost;
  self-determined exactly to the extent the probe lies in the stored
  subspace) and returns measured numbers with pass/fail each.
  headline_allowed is always False; no headline claim is emitted.
- `self_determinism.py`: self_determinism_factor() (D = <psi|P|psi>,
  the squared norm of a probe's projection onto the stored subspace),
  classical_self_determinism() (max |overlap|^2), and
  self_determinism_gap() (1 - D). D is the denominator of the Born
  weights: it says how much the system can see at all, and the
  projection entropy says how uncertain the answer is given that.
