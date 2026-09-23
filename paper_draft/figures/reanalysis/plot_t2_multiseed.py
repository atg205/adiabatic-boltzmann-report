#!/usr/bin/env python3
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

SCRATCH = Path("/home/atg205/pipcache/claude-1001/-home-atg205-Documents-Dokumentte-Uni-UPMC-stage2gl-adiabatic-boltzmann-report/596b29cd-14b9-4083-9008-5ba72cf4273b/scratchpad")
rows = json.loads((SCRATCH / "t2_n32_multiseed_independent_eval.json").read_text())

mpl.rcParams.update({
    "font.size": 12, "axes.labelsize": 12, "axes.titlesize": 12,
    "legend.fontsize": 9.5, "xtick.labelsize": 10, "ytick.labelsize": 10,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
})

SEEDS = [90, 91, 92, 93, 94]
EPSILON = 0.1
COLOR_TRAIN = "#2a78d6"
COLOR_INDEP = "#e85d5d"

fig, axes = plt.subplots(2, 3, figsize=(13, 7.6))
axes = axes.ravel()

for ax, seed in zip(axes, SEEDS):
    seed_rows = sorted([r for r in rows if r["seed"] == seed], key=lambda r: r["iteration"])
    its = [r["iteration"] for r in seed_rows]
    train_err = [r["training_log_err_per_spin"] for r in seed_rows]
    indep_err = [r["independent_err_per_spin"] for r in seed_rows]
    indep_hi = [r["independent_err_upper_bound"] for r in seed_rows]
    # symmetric-ish band around indep_err using the same half-width as the upper bound gives
    indep_lo = [max(1e-4, 2 * e - hi) for e, hi in zip(indep_err, indep_hi)]

    ax.plot(its, train_err, marker="o", color=COLOR_TRAIN, linewidth=1.8, markersize=7, label="training-log")
    ax.plot(its, indep_err, marker="s", color=COLOR_INDEP, linewidth=1.8, markersize=7, label="independent")
    ax.fill_between(its, indep_lo, indep_hi, color=COLOR_INDEP, alpha=0.18, linewidth=0)
    ax.axhline(EPSILON, color="black", linestyle="--", linewidth=1.1, alpha=0.7)

    for r in seed_rows:
        disagree = (r["training_log_err_per_spin"] < EPSILON) != r["validated_at_eps_0_1"]
        if disagree:
            ax.scatter([r["iteration"]], [r["training_log_err_per_spin"]], s=180,
                       facecolors="none", edgecolors="black", linewidths=2, zorder=5)
            ax.scatter([r["iteration"]], [r["independent_err_per_spin"]], s=180,
                       facecolors="none", edgecolors="black", linewidths=2, zorder=5)

    ax.set_yscale("log")
    ax.set_title(f"seed {seed}")
    ax.set_xlabel("SR iteration")
    ax.set_xticks(its)

axes[0].set_ylabel(r"Energy error per spin $|E-E_0|/N$")
axes[3].set_ylabel(r"Energy error per spin $|E-E_0|/N$")
axes[-1].axis("off")

handles = [
    plt.Line2D([], [], color=COLOR_TRAIN, marker="o", label="training-log energy"),
    plt.Line2D([], [], color=COLOR_INDEP, marker="s", label="independent evaluation (95% CI band)"),
    plt.Line2D([], [], color="black", linestyle="--", label=r"$\epsilon=0.1$"),
    plt.Line2D([], [], marker="o", color="none", markerfacecolor="none", markeredgecolor="black",
               markeredgewidth=2, markersize=11, linestyle="None", label="disagreement (circled)"),
]
fig.legend(handles=handles, loc="upper center", ncol=4, fontsize=10.5, bbox_to_anchor=(0.5, 1.04), frameon=False)
fig.suptitle("T2: training-log vs. independent evaluation, N=32 QPU-trained checkpoints (5 seeds)",
             fontsize=13, y=1.10)
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(SCRATCH / f"fig_t2_multiseed_disagreement.{ext}")
print("saved")
