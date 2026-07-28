#!/usr/bin/env python3
"""Finding C1: the CEM validation's reference family is not the one the sampler realises.

The sampler (report.tex L318) scales the JOINT energy, E_in = alpha * E_theta, so the
visible marginal it produces is

    p_alpha(v) ∝ exp(-alpha a.v) * prod_j 2 cosh(alpha * Theta_j),      Theta_j = b_j + (W v)_j

The validation (report.tex L365) instead fits beta in the family

    |Psi(v)|^{2 beta} ∝ exp(-beta a.v) * prod_j [2 cosh(Theta_j)]^beta

These coincide only at alpha = 1.  This script measures the bias that the mismatch alone
produces, with a PERFECTLY calibrated estimator and ZERO sampling noise: for each instance
we compute the exact p_alpha, then find the beta in the wrong family that a KL-argmin
ground truth would return, and compare it with the true alpha.

Requires: numpy.  Deterministic (fixed seed).  Runtime ~1 min for N=M=12.
"""
import itertools
import numpy as np

SEED = 7
BETA_X_GRID = (0.5, 1.0, 1.5, 2.0)   # the report's own grid, report.tex L365
WEIGHT_SD = 0.3                      # scale of the random RBM weights
N_INSTANCES = 10
BETA_SEARCH = np.linspace(0.05, 6.0, 3000)


def marginal_of_tempered_joint(V, a, b, W, alpha):
    """Visible marginal of the alpha-tempered joint - what the sampler actually gives."""
    theta = b + V @ W.T
    return np.exp(-alpha * (V @ a)) * np.prod(2 * np.cosh(alpha * theta), axis=1)


def marginal_power_family(V, a, b, W, beta):
    """|Psi(v)|^{2 beta} - the family the report's ground truth fits."""
    theta = b + V @ W.T
    return np.exp(-beta * (V @ a)) * np.prod(2 * np.cosh(theta), axis=1) ** beta


def kl_argmin_beta(V, a, b, W, alpha):
    """The beta a KL-argmin ground truth returns when the truth is p_alpha."""
    p = marginal_of_tempered_joint(V, a, b, W, alpha)
    p /= p.sum()
    best_kl, best_beta = np.inf, None
    for beta in BETA_SEARCH:
        q = marginal_power_family(V, a, b, W, beta)
        q /= q.sum()
        kl = float(np.sum(p * np.log(p / np.clip(q, 1e-300, None))))
        if kl < best_kl:
            best_kl, best_beta = kl, beta
    return best_beta


def main():
    rng = np.random.default_rng(SEED)
    print(f"seed={SEED}  weight sd={WEIGHT_SD}  instances/condition={N_INSTANCES}")
    for n in (4, 8, 12):
        V = np.array(list(itertools.product([-1.0, 1.0], repeat=n)))
        bias = {bx: [] for bx in BETA_X_GRID}
        for _ in range(N_INSTANCES):
            a = rng.normal(0, WEIGHT_SD, n)
            b = rng.normal(0, WEIGHT_SD, n)
            W = rng.normal(0, WEIGHT_SD, (n, n))
            for bx in BETA_X_GRID:
                alpha = 1.0 / bx
                bias[bx].append(kl_argmin_beta(V, a, b, W, alpha) - alpha)
        print(f"\nN = N_h = {n}")
        for bx in BETA_X_GRID:
            e = np.array(bias[bx])
            print(f"   beta_x={bx:<4} (true alpha={1/bx:.3f}): "
                  f"mean bias {e.mean():+.4f}   rms {np.sqrt((e**2).mean()):.4f}")
        allb = np.concatenate([bias[bx] for bx in BETA_X_GRID])
        print(f"   RMS over the whole grid = {np.sqrt((allb**2).mean()):.4f}"
              f"   <-- compare the report's quoted CEM RMSE 0.148 (N=8) / 0.153 (N=12)")
    print("\nReading: at beta_x = 1 the two families are identical, so the bias vanishes by")
    print("construction; away from it the reference is biased by an amount comparable to the")
    print("report's quoted RMSE. The quoted RMSE therefore cannot be read as CEM's own error.")
    print("NOTE: these are random weights, NOT the report's trained RBMs - the mismatch")
    print("magnitude on the actual instances must be re-measured with the real checkpoints.")


if __name__ == "__main__":
    main()
