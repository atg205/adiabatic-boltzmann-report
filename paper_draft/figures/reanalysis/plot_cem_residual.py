#!/usr/bin/env python3
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

REPO = Path("/home/atg205/Documents/Dokumentte/Uni/UPMC/stage2gl/adiabatic-boltzmann")
SRC = REPO / "plots" / "cem" / "cem_validation_results.json"
OUT = Path(__file__).resolve().parent

mpl.rcParams.update({
    "font.size": 12, "axes.labelsize": 12, "axes.titlesize": 12,
    "legend.fontsize": 9.5, "xtick.labelsize": 10, "ytick.labelsize": 10,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
})

d = json.loads(SRC.read_text())
fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), sharex=False, sharey=False)
colors = {"early": "#ffa600", "mid": "#bc5090", "late": "#2a78d6"}

for ax, ckpt in zip(axes, ("early", "mid", "late")):
    sub = [r for r in d if r["checkpoint"] == ckpt]
    gt = np.array([r["beta_ground_truth"] for r in sub])
    cem = np.array([r["beta_cem"] for r in sub])
    ax.scatter(gt, cem, s=14, alpha=0.5, color=colors[ckpt])
    lims = [0, max(gt.max(), cem.max()) * 1.05]
    ax.plot(lims, lims, "k--", linewidth=1.1, label="$y=x$")
    ax.axhline(50, color="red", linestyle=":", linewidth=1, alpha=0.6)
    ax.set_xlim(lims); ax.set_ylim(lims)
    ax.set_title(f"{ckpt} (n={len(sub)})")
    ax.set_xlabel(r"$\widehat\beta_{\mathrm{KL}}$ (ground truth)")
    ax.legend(loc="upper left", fontsize=8.5)
axes[0].set_ylabel(r"$\widehat\beta_{\mathrm{LS}}$ (CEM)")
fig.suptitle(r"Least-squares CEM vs.\ exact ground-truth $\beta$, by training stage "
             r"($N\in\{8,12\}$, $h\in\{0.5,1,1.5,2\}$, $\beta_x\in\{0.5,1,1.5,2\}$, 5 seeds)",
             fontsize=12.5)
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(OUT / f"fig_cem_residual_scatter.{ext}")
plt.close(fig)
print("saved fig_cem_residual_scatter.pdf")
