#!/usr/bin/env python3
"""Statistical behaviour of the CEM matching objective of report.tex Eq. (20) (L359-362).

The text defines F(beta) = sum_j (h_{j,observed} - tanh(beta Theta_j))^2 with h_observed
described as "actual samples of the hidden unit j", i.e. single +/-1 draws, whereas the
Methods version (L215-217) uses the conditional EXPECTATION <h_j>.

This script settles what the single-sample version actually does:
  (1) it is a CONSISTENT M-estimator - E[(h_j - m_j(beta))^2] = Var(h_j) + (m_j(beta_0) - m_j(beta))^2,
      whose population minimum sits at beta_0 - so it is NOT ill-posed, only noisy;
  (2) but it has a non-negligible probability of running to the search bound at small N_h,
      which happens whenever every observed h_j agrees in sign with Theta_j (then F is
      monotone decreasing in beta).

Requires: numpy.  Deterministic (fixed seed).  Runtime ~30 s.
"""
import numpy as np

SEED = 11
BETA_TRUE = 1.0
TRIALS = 4000
GRID = np.linspace(0.02, 8.0, 4000)


def fit_beta(h, theta):
    f = ((h[None, :] - np.tanh(GRID[:, None] * theta[None, :])) ** 2).sum(axis=1)
    return GRID[f.argmin()]


def main():
    rng = np.random.default_rng(SEED)
    print(f"seed={SEED}  beta_true={BETA_TRUE}  trials/condition={TRIALS}")
    print("Sign convention here follows the report as printed, <h_j> = +tanh(beta Theta_j);")
    print("the sign defect is a separate finding (C2) and does not affect these statistics.\n")
    print(f"{'N_h':>5} {'sd(Theta)':>10} {'median beta_hat':>16} {'IQR':>15}"
          f" {'P(hit bound)':>13} {'P(all h=sgn Theta)':>19}")
    for n_h in (8, 16, 64, 256):
        for sd in (0.5, 1.0):
            hats, n_bound, n_all = [], 0, 0
            for _ in range(TRIALS):
                theta = rng.normal(0, sd, n_h)
                m = np.tanh(BETA_TRUE * theta)
                h = np.where(rng.random(n_h) < (1 + m) / 2, 1.0, -1.0)
                b = fit_beta(h, theta)
                hats.append(b)
                n_bound += b >= GRID[-1] - 1e-9
                n_all += bool(np.all(h == np.sign(theta)))
            hats = np.array(hats)
            q1, q3 = np.percentile(hats, [25, 75])
            print(f"{n_h:5d} {sd:10.1f} {np.median(hats):16.3f} {f'[{q1:.2f},{q3:.2f}]':>15}"
                  f" {n_bound / TRIALS:13.3f} {n_all / TRIALS:19.3f}")
    print("\nReading:")
    print(" * median beta_hat -> beta_true as N_h grows: the single-sample objective is")
    print("   consistent, so 'the argmin is ill-posed' would be WRONG.")
    print(" * at N_h = 16 (the setting of the report's Fig. 8) the estimator saturates the")
    print("   search bound in roughly 9-22% of draws, so a single-sample implementation")
    print("   would produce many saturated draws, not the 1-in-480 the report describes.")
    print("   That mismatch is evidence the code most likely uses the averaged conditional")
    print("   mean of L215-217, and that the Eq. (20) text is what needs correcting.")


if __name__ == "__main__":
    main()
