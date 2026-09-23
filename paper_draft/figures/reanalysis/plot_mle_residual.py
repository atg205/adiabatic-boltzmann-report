#!/usr/bin/env python3
"""
Same figure as plot_cem_residual.py (fitted beta vs. exact ground-truth beta,
faceted by training checkpoint), but for the NEW conditional-MLE estimator
instead of the archived least-squares one.

The archived cem_validation_results.json cannot be reused directly: (a) it
never computed an MLE column, and (b) its Gibbs sampler was a no-op with
respect to beta_x (confirmed earlier: p(h|v)=sigma(2(b+Wv)), no rescaling),
so despite the nominal beta_x sweep, every sample in that file was actually
drawn at the model's own native beta=1 -- the *apparent* spread in
beta_ground_truth in that file comes entirely from different (N,h) trained
models, not from a real temperature sweep.

Only the N=8, h=1.0 checkpoints (early/mid/late) survive on disk. To get a
genuine, controlled sweep of TRUE beta on those checkpoints (needed to
reproduce the same kind of scatter-over-a-range plot), we deliberately
rescale (a,b,W) -> (beta_true*a, beta_true*b, beta_true*W) before sampling:
sampling the *native* (beta=1) conditionals of that rescaled model is exactly
sampling the beta_true-tempered distribution of the original model. Theta is
then evaluated at the ORIGINAL (unscaled) parameters when fitting, so the
recovered beta should equal beta_true if the estimator is correct. This is
a controlled, from-scratch test -- not a reanalysis of archived numbers.
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

OUT = Path(__file__).resolve().parent
CKPT_DIR = REPO / "checkpoints" / "cem_validation"
N = 8
N_SAMPLES = 200
SEEDS_PER_POINT = 12
GIBBS_CFG = {"n_sweeps": 10, "n_warmup": 200}
BETA_TRUE_GRID = [0.2, 0.4, 0.6, 0.8, 1.0, 1.3, 1.6, 2.0, 2.5]

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
    rbm.a = jnp.array(d["a"]); rbm.b = jnp.array(d["b"]); rbm.W = jnp.array(d["W"])


def estimate_beta_eff_mle(V, H, rbm):
    Theta = V @ rbm.W + rbm.b[None, :]

    def neg_ll(beta):
        return -float(jnp.sum(beta * H * Theta - jnp.log(2.0 * jnp.cosh(beta * Theta))))

    return float(minimize_scalar(neg_ll, bounds=(0.01, 50.0), method="bounded").x)


def ground_truth_beta(rbm_base, samples_v, beta_bounds=(0.01, 200.0)):
    """Exact KL-argmin against rbm_base's own visible marginal family."""
    configs = all_configs_jax(N)
    a_v = np.asarray(configs @ rbm_base.a)
    theta = np.asarray(configs @ rbm_base.W + rbm_base.b[None, :])
    p_emp = np.asarray(empirical_dist_jax(samples_v, N))

    def _logsumexp(a):
        c = float(np.max(a)); return c + float(np.log(np.sum(np.exp(a - c))))

    def objective(beta):
        log_unnorm = -beta * a_v + np.sum(np.log(2.0 * np.cosh(beta * theta)), axis=1)
        log_b = log_unnorm - _logsumexp(log_unnorm)
        mask = p_emp > 0
        return float(np.sum(p_emp[mask] * (np.log(p_emp[mask]) - log_b[mask])))

    return float(minimize_scalar(objective, bounds=beta_bounds, method="bounded").x)


def run():
    fig, axes = plt.subplots(2, 3, figsize=(13, 8.6))
    axes_ls, axes_mle = axes[0], axes[1]
    colors = {"early": "#ffa600", "mid": "#bc5090", "late": "#2a78d6"}

    # First pass: compute everything, find one shared log-log range across
    # ALL six panels -- a real comparison plot needs one common scale, not
    # one picked per panel, or LS's outliers and MLE's tight cluster can't
    # be read against each other honestly.
    per_tag = {}
    global_lo, global_hi = np.inf, 0.0
    for tag in ("early", "mid", "late"):
        base_rbm = FullyConnectedRBM(N, N, jax.random.PRNGKey(0))
        load_ckpt(base_rbm, CKPT_DIR / f"tfim_N8_h1.0_{tag}.pkl")

        gts, ls_vals, mle_vals = [], [], []
        for beta_true in BETA_TRUE_GRID:
            scaled = FullyConnectedRBM(N, N, jax.random.PRNGKey(0))
            scaled.a = beta_true * base_rbm.a
            scaled.b = beta_true * base_rbm.b
            scaled.W = beta_true * base_rbm.W

            for seed in range(SEEDS_PER_POINT):
                sampler = ClassicalSampler("gibbs")
                sampler._key = jax.random.PRNGKey(int(beta_true * 1000) * 100 + seed)
                v, h = sampler.sample(scaled, N_SAMPLES, config=GIBBS_CFG,
                                       return_hidden=True, return_jax=True)
                V = jnp.asarray(v, dtype=jnp.float64)
                H = jnp.asarray(h, dtype=jnp.float64)
                gts.append(ground_truth_beta(base_rbm, V))
                ls_vals.append(estimate_beta_eff_cem(V, H, base_rbm))
                mle_vals.append(estimate_beta_eff_mle(V, H, base_rbm))

        gts, ls_vals, mle_vals = np.array(gts), np.array(ls_vals), np.array(mle_vals)
        per_tag[tag] = (gts, ls_vals, mle_vals)
        global_lo = min(global_lo, gts.min(), ls_vals.min(), mle_vals.min())
        global_hi = max(global_hi, gts.max(), ls_vals.max(), mle_vals.max())

    lims = [global_lo * 0.8, global_hi * 1.2]

    for ax_ls, ax_mle, tag in zip(axes_ls, axes_mle, ("early", "mid", "late")):
        gts, ls_vals, mle_vals = per_tag[tag]

        for ax, vals, ylabel, label in ((ax_ls, ls_vals, r"$\widehat\beta_{\mathrm{LS}}$", "LS"),
                                         (ax_mle, mle_vals, r"$\widehat\beta_{\mathrm{MLE}}$", "MLE")):
            nhit = int((vals > 49).sum())
            resid = vals - gts
            ax.scatter(gts, vals, s=16, alpha=0.5, color=colors[tag])
            ax.plot(lims, lims, "k--", linewidth=1.1, label="$y=x$")
            ax.set_xscale("log"); ax.set_yscale("log")
            ax.set_xlim(lims); ax.set_ylim(lims)
            ax.set_title(f"{label} -- {tag}  ({nhit}/{len(gts)} boundary hits)", fontsize=11.5)
            ax.set_xlabel(r"$\widehat\beta_{\mathrm{KL}}$ (ground truth)")
            ax.set_ylabel(ylabel)
            ax.legend(loc="upper left", fontsize=8.5)
            ax.text(0.97, 0.05, f"median bias {np.median(resid):+.3f}",
                    transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5,
                    color="#444444")

        resid_ls = ls_vals - gts
        resid_mle = mle_vals - gts
        nhit_ls = int((ls_vals > 49).sum())
        nhit_mle = int((mle_vals > 49).sum())
        print(f"{tag:6s} LS : mean_bias={resid_ls.mean():+.3f} RMSE={np.sqrt((resid_ls**2).mean()):.3f} "
              f"median_bias={np.median(resid_ls):+.3f} boundary_hits={nhit_ls}/{len(gts)}")
        print(f"{tag:6s} MLE: mean_bias={resid_mle.mean():+.3f} RMSE={np.sqrt((resid_mle**2).mean()):.3f} "
              f"median_bias={np.median(resid_mle):+.3f} boundary_hits={nhit_mle}/{len(gts)}")

    fig.suptitle(r"$\widehat\beta_{\mathrm{LS}}$ (top) vs.\ $\widehat\beta_{\mathrm{MLE}}$ (bottom) against exact ground truth"
                 "\n" r"controlled $\beta_{\mathrm{true}}$ sweep, $N=8$, $h=1.0$, 12 seeds/point",
                 fontsize=13)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_cem_residual_controlled_comparison.{ext}")
    print("saved fig_cem_residual_controlled_comparison.pdf")


if __name__ == "__main__":
    run()
