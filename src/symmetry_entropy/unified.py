"""Unified claim: four falsifiable statements, measured, no headline.

This module runs the four claims and returns measured numbers with a
pass/fail for each. It emits no headline claim: headline_allowed is
always False, exactly like symmetry-quantum-flip-membrane's
full_science.py.

(a) Distinguishability is bounded by orbit entropy: in closed-orbit
    mode, the number of distinct recalls across a pattern's orbit
    equals the orbit size. The projection resolves exactly as much as
    the orbit entropy allows -- no more.
(b) The projection's kernel is invisible: a probe orthogonal to every
    stored pattern has all Born weights 0 and is_kernel True. The
    projection cannot see it at all.
(c) The projected world has higher entropy than the underlying state
    by the asymmetry cost -- measured in the classical orbit case AND
    the quantum twirl case:
    - classical: a single definite pattern has entropy 0; the uniform
      distribution over its orbit has entropy log2(|orbit|); the gap
      equals the orbit entropy.
    - quantum: S(twirl(rho)) - S(rho) equals log2 of the state's orbit
      size under the group (|0> under {I, X}: 1 bit = log2 2; |+>: 0
      bits = log2 1).
(d) The projection is self-determined exactly to the extent the probe
    lies in the stored subspace: D = <psi|P|psi> is 1 for a clean
    stored probe (fully self-determined, projection entropy 0), 0 for
    a kernel probe (invisible, all weights 0), and strictly between 0
    and 1 for a noisy or random probe. The classical analogue holds
    too: every transform of a stored pattern has D = 1 in closed-orbit
    mode, while a transformed probe in base-only mode has D < 1 --
    the missing part is exactly the orbit information base-only mode
    never stored.

These are measurements on synthetic classical code. They are not a
proof about physical reality; see REPORT.md, "Honest limits".
"""

import math

from .asymmetry import (
    KET_PLUS,
    KET_ZERO,
    PAULI_GROUP_IX,
    asymmetry_cost,
    ket_to_dm,
    state_orbit_size,
    von_neumann_entropy,
    twirl,
)
from .orbit import (
    BASE_PATTERNS,
    FALSIFIED_PATTERNS,
    HolographicMembrane,
    closed_orbit_patterns,
    distinct_recalls,
    orbit,
    orbit_entropy,
)
from .projection_entropy import (
    HolographicMembrane as QuantumMembrane,
)
from .projection_entropy import (
    bell_phi_minus,
    bell_phi_plus,
    bell_psi_minus,
    bell_psi_plus,
    born_weights,
    is_kernel,
    noisy,
    projection_entropy,
    random_state,
)
from .self_determinism import (
    classical_self_determinism,
    self_determinism_factor,
)

HEADLINE_NOTE = (
    "No headline claim is emitted. This is a synthetic toy only; "
    "results apply only to the recorded seeds, patterns, and noise "
    "levels."
)


def _closed_orbit_membrane_all():
    """One membrane storing the closed orbits of all 7 patterns.

    32 asymmetric-orbit patterns + blocks (2) + ring (1) + cross (1)
    = 36 distinct stored patterns. The orbits do not collide, so every
    transform recalls its own stored name at overlap 1.0.
    """
    patterns = dict(closed_orbit_patterns())
    for name, pat in FALSIFIED_PATTERNS.items():
        for op in ("identity", "rot90", "rot180", "rot270",
                   "flip_h", "flip_v", "transpose", "anti_transpose"):
            from .orbit import apply_op
            patterns[f"{name}@{op}"] = apply_op(pat, op)
    return HolographicMembrane(patterns)


def _classical_gap(pattern):
    """(underlying, projected, gap) for one classical pattern.

    Underlying: the single definite pattern, entropy 0 bits.
    Projected: the uniform distribution over its orbit, entropy
    log2(|orbit|) bits. Gap = orbit entropy.
    """
    n = len(orbit(pattern))
    underlying = 0.0
    # + 0.0 normalizes a -0.0 result to 0.0 for clean output.
    projected = -sum((1.0 / n) * math.log2(1.0 / n) for _ in range(n)) + 0.0
    return underlying, projected, projected - underlying


def _quantum_gap(psi, unitaries):
    """(S(rho), S(twirl), cost, log2 orbit size) for one quantum state."""
    rho = ket_to_dm(psi)
    s_rho = von_neumann_entropy(rho)
    s_twirl = von_neumann_entropy(twirl(rho, unitaries))
    cost = asymmetry_cost(rho, unitaries)
    log2_orbit = math.log2(state_orbit_size(psi, unitaries))
    return s_rho, s_twirl, cost, log2_orbit


def unified_claim():
    """Run the four falsifiable statements; return measured numbers."""
    tol = 1e-9
    result = {"version": "0.1.0", "headline_allowed": False,
              "headline_note": HEADLINE_NOTE}

    # --- (a) Distinguishability is bounded by orbit entropy ---
    membrane = _closed_orbit_membrane_all()
    claim_a = {"patterns": {}, "pass": True}
    all_patterns = dict(BASE_PATTERNS)
    all_patterns.update(FALSIFIED_PATTERNS)
    for name, pat in all_patterns.items():
        o_size = len(orbit(pat))
        o_ent = orbit_entropy(pat)
        d_rec = distinct_recalls(membrane, pat)
        ok = (d_rec == o_size)
        claim_a["patterns"][name] = {
            "orbit_size": o_size,
            "orbit_entropy": o_ent,
            "distinct_recalls": d_rec,
            "pass": ok,
        }
        claim_a["pass"] = claim_a["pass"] and ok
    result["claim_a"] = claim_a

    # --- (b) The projection's kernel is invisible ---
    qmem = QuantumMembrane([bell_phi_plus(), bell_phi_minus(), bell_psi_plus()])
    psi_minus = bell_psi_minus()
    weights = born_weights(qmem, psi_minus)
    kernel = is_kernel(qmem, psi_minus)
    claim_b = {
        "probe": "Psi- (orthogonal to all stored patterns)",
        "weights": weights,
        "is_kernel": kernel,
        "projection_entropy": projection_entropy(qmem, psi_minus),
        "pass": bool(kernel and all(w == 0.0 for w in weights)),
    }
    result["claim_b"] = claim_b

    # --- (c) The projected world has higher entropy by the asymmetry cost ---
    claim_c = {"classical": {}, "quantum": {}, "pass": True}
    for name in ("alpha", "ring"):
        pat = all_patterns[name]
        underlying, projected, gap = _classical_gap(pat)
        o_ent = orbit_entropy(pat)
        ok = abs(gap - o_ent) < tol
        claim_c["classical"][name] = {
            "underlying_entropy": underlying,
            "projected_entropy": projected,
            "gap": gap,
            "orbit_entropy": o_ent,
            "pass": ok,
        }
        claim_c["pass"] = claim_c["pass"] and ok
    for label, psi in (("|0>", KET_ZERO), ("|+>", KET_PLUS)):
        s_rho, s_twirl, cost, log2_orbit = _quantum_gap(psi, PAULI_GROUP_IX)
        ok = abs(cost - log2_orbit) < tol
        claim_c["quantum"][label] = {
            "S_rho": s_rho,
            "S_twirl": s_twirl,
            "asymmetry_cost": cost,
            "log2_orbit_size": log2_orbit,
            "pass": ok,
        }
        claim_c["pass"] = claim_c["pass"] and ok
    result["claim_c"] = claim_c

    # --- (d) The projection is self-determined to the extent the probe lies in the stored subspace ---
    claim_d = {"quantum": {}, "classical": {}, "pass": True}
    # Quantum: D = 1 for a clean stored probe, 0 for the kernel, strictly between for noisy/random.
    q_cases = [
        ("Phi+ clean", bell_phi_plus(), 1.0, True),
        ("Phi+ noisy sigma=0.25 seed 11", noisy(bell_phi_plus(), 0.25, 11), 0.843355, None),
        ("Phi+ noisy sigma=0.75 seed 11", noisy(bell_phi_plus(), 0.75, 11), 0.567154, None),
        ("Psi- clean (kernel)", bell_psi_minus(), 0.0, True),
        ("Haar-random seed 7", random_state(2, 7), 0.909800, None),
        ("Haar-random seed 42", random_state(2, 42), 0.192721, None),
    ]
    for label, probe, expected, is_endpoint in q_cases:
        d = self_determinism_factor(qmem, probe)
        if is_endpoint:
            ok = abs(d - expected) < tol
        else:
            ok = abs(d - expected) < 1e-3 and 0.0 < d < 1.0
        claim_d["quantum"][label] = {"D": d, "expected": expected, "pass": ok}
        claim_d["pass"] = claim_d["pass"] and ok
    # Quantum endpoints tie D to the other two quantities: D = 1 goes with
    # projection entropy 0; D = 0 goes with kernel True and all weights 0.
    claim_d["quantum"]["Phi+ clean"]["projection_entropy"] = projection_entropy(qmem, bell_phi_plus())
    claim_d["quantum"]["Psi- clean (kernel)"]["is_kernel"] = is_kernel(qmem, bell_psi_minus())
    # Classical: D = 1 for every stored transform in closed-orbit mode;
    # D < 1 for a transformed probe in base-only mode.
    base_mem = HolographicMembrane(dict(BASE_PATTERNS))
    from .orbit import apply_op as _apply_op
    c_probes = [
        ("alpha clean (closed-orbit)", membrane, BASE_PATTERNS["alpha"], 1.0),
        ("alpha rot90 (closed-orbit)", membrane, _apply_op(BASE_PATTERNS["alpha"], "rot90"), 1.0),
        ("alpha rot90 (base-only)", base_mem, _apply_op(BASE_PATTERNS["alpha"], "rot90"), 0.25),
        ("alpha rot180 (base-only)", base_mem, _apply_op(BASE_PATTERNS["alpha"], "rot180"), 0.25),
    ]
    for label, mem, probe, expected in c_probes:
        d = classical_self_determinism(mem, probe)
        ok = abs(d - expected) < tol
        claim_d["classical"][label] = {"D": d, "expected": expected, "pass": ok}
        claim_d["pass"] = claim_d["pass"] and ok
    result["claim_d"] = claim_d

    result["overall_pass"] = bool(
        claim_a["pass"] and claim_b["pass"] and claim_c["pass"] and claim_d["pass"])
    return result


def _cli():
    """Print the unified claim as JSON (console entry point)."""
    import json
    print(json.dumps(unified_claim(), indent=2, sort_keys=True))
    return 0
