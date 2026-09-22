#!/usr/bin/env python3
"""
T1: numerically compare the conditional-MLE beta_eff estimator (new, this
paper) against the existing pooled least-squares CEM estimator, on FRESH
Gibbs samples drawn from the three surviving cem_validation_sweep.py
checkpoints (N=8, h=1.0, early/mid/late). CPU only -- trivial problem size.

The Gibbs sampler here targets the RBM's own exact |Psi(v)|^2 at implicit
beta=1 with NO rescaling (confirmed by reading src/sampler.py's
_gibbs_sample: p(h|v)=sigma(2(b+Wv)), no beta_x anywhere) -- so the true
generating beta is EXACTLY 1, not merely estimated. This lets us score both
estimators against a known answer instead of against another estimate.
"""
import os
os.environ.setdefault("JAX_PLATFORM_NAME", "cpu")

import pickle
import sys
from pathlib import Path

import numpy as np
import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt
import matplotlib as mpl

REPO = Path("/home/atg205/Documents/Dokumentte/Uni/UPMC/stage2gl/adiabatic-boltzmann")
sys.path.insert(0, str(REPO / "src"))
from model import FullyConnectedRBM  # noqa: E402
from sampler import ClassicalSampler  # noqa: E402
from encoder import estimate_beta_eff_cem  # noqa: E402
from kl_utils import all_configs_jax, empirical_dist_jax  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
CKPT_DIR = REPO / "checkpoints" / "cem_validation"
N = 8
TRUE_BETA = 1.0
N_SAMPLES = 200
N_SEEDS = 150
GIBBS_CFG = {"n_sweeps": 10, "n_warmup": 200}

mpl.rcParams.update({
    "font.size": 12, "axes.labelsize": 12, "axes.titlesize": 12,
    "legend.fontsize": 9.5, "xtick.labelsize": 10, "ytick.labelsize": 10,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
})


def load_ckpt(rbm, path):
    with open(path, "rb") as f:
        d = pickle.load(f)
    rbm.a = jnp.array(d["a"])
    rbm.b = jnp.array(d["b"])
    rbm.W = jnp.array(d["W"])


def estimate_beta_eff_mle(V, H, rbm):
    """Conditional-MLE score-equation estimator (Eq. score, thermometry.tex),
    solved as the argmax of the concave conditional log-likelihood."""
    Theta = V @ rbm.W + rbm.b[None, :]

    def neg_ll(beta):
        return -float(jnp.sum(beta * H * Theta - jnp.log(2.0 * jnp.cosh(beta * Theta))))

    result = minimize_scalar(neg_ll, bounds=(0.01, 50.0), method="bounded")
    return float(result.x)


def ground_truth_beta(rbm, samples_v, beta_bounds=(0.01, 200.0)):
    """Exact KL-argmin against the true visible marginal (same construction
    as cem_validation_sweep.py's _ground_truth_beta)."""
    configs = all_configs_jax(N)
    a_v = np.asarray(configs @ rbm.a)
    theta = np.asarray(configs @ rbm.W + rbm.b[None, :])
    p_emp = np.asarray(empirical_dist_jax(samples_v, N))

    def _logsumexp(a):
        c = float(np.max(a))
        return c + float(np.log(np.sum(np.exp(a - c))))

    def objective(beta):
        log_unnorm = -beta * a_v + np.sum(np.log(2.0 * np.cosh(beta * theta)), axis=1)
        log_b = log_unnorm - _logsumexp(log_unnorm)
        mask = p_emp > 0
        return float(np.sum(p_emp[mask] * (np.log(p_emp[mask]) - log_b[mask])))

    result = minimize_scalar(objective, bounds=beta_bounds, method="bounded")
    return float(result.x)


def run():
    results = {}
    for tag in ("early", "mid", "late"):
        path = CKPT_DIR / f"tfim_N8_h1.0_{tag}.pkl"
        rbm = FullyConnectedRBM(N, N, jax.random.PRNGKey(0))
        load_ckpt(rbm, path)

        ls_vals, mle_vals, gt_vals = [], [], []
        for seed in range(N_SEEDS):
            sampler = ClassicalSampler("gibbs")
            sampler._key = jax.random.PRNGKey(1000 * (hash(tag) % 97) + seed)
            v, h = sampler.sample(rbm, N_SAMPLES, config=GIBBS_CFG,
                                   return_hidden=True, return_jax=True)
            V = jnp.asarray(v, dtype=jnp.float64)
            H = jnp.asarray(h, dtype=jnp.float64)
            ls_vals.append(estimate_beta_eff_cem(V, H, rbm))
            mle_vals.append(estimate_beta_eff_mle(V, H, rbm))
            gt_vals.append(ground_truth_beta(rbm, V))

        results[tag] = dict(ls=np.array(ls_vals), mle=np.array(mle_vals), gt=np.array(gt_vals))
        print(f"[{tag}] true_beta={TRUE_BETA}  "
              f"LS: mean={np.mean(ls_vals):.3f} std={np.std(ls_vals):.3f} bias={np.mean(ls_vals)-TRUE_BETA:+.3f}  "
              f"MLE: mean={np.mean(mle_vals):.3f} std={np.std(mle_vals):.3f} bias={np.mean(mle_vals)-TRUE_BETA:+.3f}  "
              f"GTfit: mean={np.mean(gt_vals):.3f} std={np.std(gt_vals):.3f}")

    # Figure: boxplot-style comparison per checkpoint stage
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharey=True)
    for ax, tag in zip(axes, ("early", "mid", "late")):
        r = results[tag]
        data = [r["ls"], r["mle"], r["gt"]]
        bp = ax.boxplot(data, labels=[r"$\hat\beta_{\mathrm{LS}}$", r"$\hat\beta_{\mathrm{MLE}}$", r"$\hat\beta_{\mathrm{KL}}$ (exact ref.)"],
                         patch_artist=True, widths=0.55, showmeans=True)
        colors = ["#bc5090", "#2a78d6", "#898781"]
        for patch, c in zip(bp["boxes"], colors):
            patch.set_facecolor(c)
            patch.set_alpha(0.35)
        ax.axhline(TRUE_BETA, color="black", linestyle="--", linewidth=1.2, label=r"true $\beta=1$")
        ax.set_title(f"{tag} (N={N_SAMPLES} samples, {N_SEEDS} seeds)")
        ax.legend(loc="upper right", fontsize=8.5)
    axes[0].set_ylabel(r"Fitted $\widehat\beta_{\mathrm{eff}}$")
    fig.suptitle(r"Conditional-MLE vs.\ least-squares $\beta_{\mathrm{eff}}$: known-truth test ($N=8$, $h=1.0$, Gibbs samples at exact $\beta=1$)",
                 fontsize=12.5)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig_mle_vs_ls_known_truth.{ext}"))
    plt.close(fig)
    print("\nsaved fig_mle_vs_ls_known_truth.pdf")


if __name__ == "__main__":
    run()
