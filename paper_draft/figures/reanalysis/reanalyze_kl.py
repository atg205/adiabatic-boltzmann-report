#!/usr/bin/env python3
"""
Reanalysis of archived kl_exact (exact-enumeration KL divergence between the
per-iteration empirical sample histogram and the model's own exact Born
distribution) at N=8,16, where it is computed (KL_EXACT_MAX_N=16 in
src/encoder.py). READS ONLY archived result files. No new experiments.

Produces two figures:
  A) solver comparison: Metropolis/Gibbs/SA/FPGA/Pegasus(+CEM)/Zephyr(+CEM)
  B) CEM ablation: Pegasus and Zephyr, cem=0 vs cem=1
"""
import glob
import gzip
import json
import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

REPO = "/home/atg205/Documents/Dokumentte/Uni/UPMC/stage2gl/adiabatic-boltzmann"
OUT = os.path.dirname(os.path.abspath(__file__))

mpl.rcParams.update({
    "font.size": 12, "axes.labelsize": 12, "axes.titlesize": 12,
    "legend.fontsize": 9, "xtick.labelsize": 10, "ytick.labelsize": 10,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
})

COLORS = {
    "Metropolis": "#2a78d6", "Gibbs": "#008300", "Simulated Annealing": "#6a3d9a",
    "FPGA": "#ffa600", "Pegasus (+CEM)": "#bc5090", "Zephyr (+CEM)": "#ef5675",
    "Pegasus (no CEM)": "#7a3350", "Zephyr (no CEM)": "#8f232f",
}
MARKERS = {
    "Metropolis": "o", "Gibbs": "s", "Simulated Annealing": "v", "FPGA": "X",
    "Pegasus (+CEM)": "D", "Zephyr (+CEM)": "h",
    "Pegasus (no CEM)": "d", "Zephyr (no CEM)": "p",
}


def load(pattern):
    out = []
    for f in sorted(glob.glob(pattern)):
        with gzip.open(f) as fh:
            out.append(json.load(fh))
    return out


def _matched(recs, n):
    return [r for r in recs if r["config"]["n_hidden"] == n
            and abs(r["config"]["learning_rate"] - 0.08) < 1e-9
            and abs(r["config"]["regularization"] - 0.05) < 1e-9
            and r["config"]["n_samples"] == 200
            and r["config"]["iterations"] == 100][:20]


def mcmc_recs(solver, n):
    pat = (f"{REPO}/results/tfim_1d/{n}/custom/{solver}/"
           f"result_1d_h0.5_rbmfull_nh{n}_lr0.08_reg0.05_ns200_seed*_iter100_cem0_sigma1.0.json.gz")
    return _matched(load(pat), n)


def fpga_recs(n):
    pat = f"{REPO}/results/tfim_1d/{n}/fpga/*/result_*_seed*_iter*"
    return _matched(load(pat), n)


def dwave_recs(method, n, cem):
    pat = (f"{REPO}/results/tfim_1d/{n}/dimod/{method}/"
           f"result_1d_h0.5_rbmfull_nh{n}_lr0.08_reg0.05_ns200_seed*_iter100_cem{cem}_sigma1.0.json.gz")
    return _matched(load(pat), n)


def kl_matrix(recs):
    """(n_seeds, 100) array of kl_exact; rows with any None are dropped."""
    rows = []
    for r in recs:
        kl = r["history"]["kl_exact"]
        if any(v is None for v in kl):
            continue
        rows.append(kl)
    return np.array(rows, dtype=float) if rows else np.empty((0, 100))


def median_iqr_curve(mat):
    med = np.median(mat, axis=0)
    lo = np.percentile(mat, 25, axis=0)
    hi = np.percentile(mat, 75, axis=0)
    return med, lo, hi


def plot_group(ax, groups, n_focus):
    for label, recs in groups:
        if not recs:
            continue
        mat = kl_matrix(recs)
        if mat.size == 0:
            continue
        med, lo, hi = median_iqr_curve(mat)
        it = np.arange(1, len(med) + 1)
        ax.plot(it, med, color=COLORS[label], marker=MARKERS[label], markevery=10,
                markersize=5, linewidth=1.7, label=f"{label} (n={mat.shape[0]})")
        ax.fill_between(it, lo, hi, color=COLORS[label], alpha=0.15, linewidth=0)
    ax.set_yscale("log")
    ax.set_xlabel("SR iteration")
    ax.set_title(f"$N={n_focus}$")


def figure_solver_comparison(sizes=(8, 16)):
    fig, axes = plt.subplots(1, len(sizes), figsize=(6.2 * len(sizes), 5.0), sharey=False)
    axes = np.atleast_1d(axes)
    for ax, n in zip(axes, sizes):
        groups = [
            ("Metropolis", mcmc_recs("metropolis", n)),
            ("Gibbs", mcmc_recs("gibbs", n)),
            ("Simulated Annealing", mcmc_recs("simulated_annealing", n)),
            ("FPGA", fpga_recs(n)),
            ("Pegasus (+CEM)", dwave_recs("pegasus", n, 1)),
            ("Zephyr (+CEM)", dwave_recs("zephyr", n, 1)),
        ]
        plot_group(ax, groups, n)
    axes[0].set_ylabel(r"$D_{\mathrm{KL}}(\hat q \,\|\, \pi_\theta)$ (exact enumeration)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=6, fontsize=9,
               bbox_to_anchor=(0.5, 1.06), frameon=False)
    fig.suptitle(r"Sampling fidelity vs.\ training iteration ($h=0.5$, exact $D_{\mathrm{KL}}$ to the model's own Born distribution)",
                 fontsize=12.5, y=1.13)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig_kl_exact_solver_comparison.{ext}"))
    plt.close(fig)
    print("[A] saved fig_kl_exact_solver_comparison.pdf")


def figure_cem_ablation(sizes=(8, 16)):
    fig, axes = plt.subplots(1, len(sizes), figsize=(6.2 * len(sizes), 5.0), sharey=False)
    axes = np.atleast_1d(axes)
    for ax, n in zip(axes, sizes):
        groups = [
            ("Pegasus (no CEM)", dwave_recs("pegasus", n, 0)),
            ("Pegasus (+CEM)", dwave_recs("pegasus", n, 1)),
            ("Zephyr (no CEM)", dwave_recs("zephyr", n, 0)),
            ("Zephyr (+CEM)", dwave_recs("zephyr", n, 1)),
        ]
        plot_group(ax, groups, n)
    axes[0].set_ylabel(r"$D_{\mathrm{KL}}(\hat q \,\|\, \pi_\theta)$ (exact enumeration)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=9.5,
               bbox_to_anchor=(0.5, 1.08), frameon=False)
    fig.suptitle(r"Effect of pooled CEM correction on QPU sampling fidelity ($h=0.5$)",
                 fontsize=12.5, y=1.15)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig_kl_exact_cem_ablation.{ext}"))
    plt.close(fig)
    print("[B] saved fig_kl_exact_cem_ablation.pdf")

    # numeric summary at final iteration
    print("\nFinal-iteration (median across seeds) kl_exact:")
    for n in sizes:
        for method in ("pegasus", "zephyr"):
            for cem in (0, 1):
                recs = dwave_recs(method, n, cem)
                mat = kl_matrix(recs)
                if mat.size == 0:
                    continue
                final = mat[:, -1]
                print(f"  N={n:3d} {method:8s} cem={cem}  median_final_kl={np.median(final):.4f}  n_seeds={mat.shape[0]}")


if __name__ == "__main__":
    figure_solver_comparison()
    figure_cem_ablation()
