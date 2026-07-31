#!/usr/bin/env python3
"""Corrected CEM validation, replacing the broken methodology of report.tex L360-370 (Finding F1).

The report's validation fits an INDEPENDENT ground-truth beta against the wrong family
(|Psi(v)|^{2*beta}, see verify/cem_family.py) and then compares CEM's estimate to that.
This conflates two unrelated things: (a) the family mismatch, and (b) CEM's own error.

The fix needs no independent reference family at all. CEM's estimator is meant to recover
the beta that a sampler is ACTUALLY drawing conditional hidden units at. So: generate
conditional hidden samples at a KNOWN beta_true (this stands in for the LSB/QPU sampler
at a known effective inverse temperature), run CEM's matching step on them, and compare
directly to beta_true. No auxiliary family, no mismatch, no bug.

Energy convention matches report.tex as fixed in the working tree (E = a.v - b.h - h.W.v,
<h_j|v> = tanh(beta * Theta_j), Theta_j = b_j + (W v)_j).

Reports, for the report's own grid (N=N_h in {8,12}, beta_true in {0.5,1,1.5,2}, 5 seeds):
  (1) the NOISELESS limit (N_c -> infinity, i.e. matching against the exact conditional
      expectation of L215-217): bias should vanish at EVERY beta_true, not just beta=1.
      This is the direct fix for F1, and is checked by an assertion, not just printed.
  (2) finite N_c (single-sample, and N_c=16 matching Fig. 8/11's hidden-unit count):
      the realistic sampling-noise RMSE and search-bound-saturation rate CEM would show
      once validated correctly - this is the number that should replace the report's
      0.148/0.153 RMSE, once re-run on the REAL trained checkpoints (not available in
      this repository - see caveat printed at the end).

Requires: numpy.  Deterministic (fixed seed).  Runtime ~20 s.
"""
import itertools
import numpy as np

SEED = 23
WEIGHT_SD = 0.3
N_SEEDS = 5
BETA_GRID = (0.5, 1.0, 1.5, 2.0)     # report's own beta_x grid, report.tex L365
GRID = np.linspace(0.02, 8.0, 4000)  # search grid for beta_hat (mirrors scipy minimize_scalar)


def fit_beta(h_bar, theta):
    f = ((h_bar[None, :] - np.tanh(GRID[:, None] * theta[None, :])) ** 2).sum(axis=1)
    return GRID[f.argmin()]


def conditional_draw(rng, theta, beta, n_c):
    """n_c i.i.d. +/-1 draws per hidden unit at the given beta; returns the empirical mean."""
    p_plus = 0.5 * (1 + np.tanh(beta * theta))
    draws = np.where(rng.random((n_c, theta.shape[0])) < p_plus, 1.0, -1.0)
    return draws.mean(axis=0)


def run_grid(rng, n, n_c):
    """n_c=None means the noiseless limit (exact conditional expectation)."""
    bias = {bt: [] for bt in BETA_GRID}
    bound_hits = 0
    total = 0
    for _ in range(N_SEEDS):
        a = rng.normal(0, WEIGHT_SD, n)      # unused (a only shifts the visible marginal)
        b = rng.normal(0, WEIGHT_SD, n)
        W = rng.normal(0, WEIGHT_SD, (n, n))
        v = rng.choice([-1.0, 1.0], size=n)  # one condition vector per instance
        theta = b + W @ v
        for beta_true in BETA_GRID:
            if n_c is None:
                h_bar = np.tanh(beta_true * theta)   # exact conditional expectation, L215-217
            else:
                h_bar = conditional_draw(rng, theta, beta_true, n_c)
            beta_hat = fit_beta(h_bar, theta)
            bias[beta_true].append(beta_hat - beta_true)
            bound_hits += beta_hat >= GRID[-1] - 1e-9
            total += 1
    return bias, bound_hits / total


def self_check():
    """The methodology fix: unlike the broken family, bias must vanish at EVERY beta_true,
    not just beta_true=1. This is what actually settles Finding F1."""
    rng = np.random.default_rng(SEED)
    bias, _ = run_grid(rng, n=8, n_c=None)
    for beta_true, errs in bias.items():
        worst = max(abs(e) for e in errs)
        assert worst < 0.02, (
            f"noiseless CEM should recover beta_true={beta_true} exactly "
            f"(within grid resolution); got max |bias|={worst:.4f}"
        )
    print("self-check passed: noiseless bias < 0.02 at every beta_true in "
          f"{BETA_GRID}, including beta_true != 1 (fixes the F1 family bug).\n")


def main():
    self_check()
    print(f"seed={SEED}  weight sd={WEIGHT_SD}  seeds/condition={N_SEEDS}\n")

    for n in (8, 12):
        print(f"N = N_h = {n}")
        rng = np.random.default_rng(SEED)
        bias_exact, _ = run_grid(rng, n, n_c=None)
        for beta_true in BETA_GRID:
            e = np.array(bias_exact[beta_true])
            print(f"   beta_true={beta_true:<4}  noiseless bias {e.mean():+.5f}  "
                  f"rms {np.sqrt((e ** 2).mean()):.5f}   (should be ~0 at every beta_true)")

        for n_c, label in ((1, "single-sample (Eq. 20 as printed)"), (16, "N_c=16 (Fig. 8/11 scale)")):
            rng = np.random.default_rng(SEED)
            bias_noisy, bound_rate = run_grid(rng, n, n_c=n_c)
            allb = np.concatenate([bias_noisy[bt] for bt in BETA_GRID])
            print(f"   {label}: RMS over the whole grid = {np.sqrt((allb ** 2).mean()):.4f}"
                  f"   bound-saturation rate = {bound_rate:.3f}")
        print()

    print("Reading:")
    print(" * The noiseless bias is ~0 at EVERY beta_true (not just beta_true=1) - this is")
    print("   the actual fix for F1: no independent reference family is needed, so there is")
    print("   nothing left to be biased by a family mismatch.")
    print(" * The finite-N_c RMS/bound-saturation numbers are what a corrected validation")
    print("   would report in place of the current 0.148/0.153 RMSE and the '1 saturated")
    print("   draw out of 480' claim - once N_c is stated (Finding M2).")
    print()
    print("CAVEAT: weights here are synthetic (random, seed-fixed), NOT the report's")
    print("trained RBM checkpoints, which are not present in this repository (no model")
    print("weights are committed - only scalar summary stats in figures/sparsity/*.json).")
    print("The methodology below is correct and reproducible; re-run it against the real")
    print("checkpoints (same fit_beta/conditional_draw logic, real a/b/W, real v samples,")
    print("real N_c) to get the report's actual corrected Fig. 7 numbers.")


if __name__ == "__main__":
    main()
