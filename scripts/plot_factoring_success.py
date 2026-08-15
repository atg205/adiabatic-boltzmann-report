#!/usr/bin/env python3
"""
Reproduction of Fig. 4a from Willsch et al., "The State of Factoring on
Quantum Computers", arXiv:2410.14397 -- success frequency of three D-Wave
QUBO factorisation encodings (Direct, MC, CFA) vs. the number of unknown
bits l = l_p* + l_q*, against the uniform-random-guessing baseline 2^-l.

Data are the published success-rate tables from the companion repository
https://jugit.fz-juelich.de/qip/jupsifactoring (data/final_*_success.pckl):
for each l, `success_rate` is the mean success frequency (%) over ~10
randomly drawn semiprimes, and q25/q75 are the 25th/75th percentiles of
that per-semiprime success frequency. Values are embedded here directly
(small, fixed, published tables) rather than re-fetched at build time.

Usage:
    python scripts/plot_factoring_success.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot_style import AQUA, BLUE, FIGSIZE, ORANGE, RED, setup_style, style_legend

_ROOT = Path(__file__).resolve().parent.parent
_OUT = _ROOT / "figures" / "factoring_success.pdf"

# l, success_rate (%), q25 (%), q75 (%) -- from data/final_*_success.pckl
DIRECT = dict(
    l=[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
    rate=[47.545833, 18.747037, 10.627619, 6.351429, 1.605476, 1.082292,
          7.132000, 0.273750, 0.126667, 0.052727, 0.398750, 0.011111,
          0.267143, 0.003333],
    q25=[46.102083, 16.350000, 5.036667, 2.515000, 0.930000, 0.475000,
         0.120000, 0.037500, 0.020000, 0.000000, 0.000000, 0.000000,
         0.000000, 0.000000],
    q75=[48.989583, 17.150000, 13.140000, 8.595000, 2.079167, 1.556875,
         0.852500, 0.230000, 0.125000, 0.020000, 0.040000, 0.020000,
         0.000000, 0.000000],
)
MC = dict(
    l=[8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20],
    rate=[18.550000, 5.351000, 1.820000, 0.635000, 0.420625, 0.113333,
          0.074545, 0.025455, 0.006000, 0.004375, 0.004545, 0.002000],
    q25=[18.020000, 2.555000, 0.927500, 0.205000, 0.100000, 0.047500,
         0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
    q75=[19.080000, 7.280000, 2.185000, 0.692500, 0.640000, 0.155000,
         0.075000, 0.025000, 0.007500, 0.010000, 0.005000, 0.000000],
)
CFA = dict(
    l=[4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22],
    rate=[83.240000, 71.440000, 64.740000, 40.195000, 32.248571, 6.080000,
          3.286923, 1.048421, 0.468590, 0.514667, 0.171429, 0.073846,
          0.005455, 0.008889, 0.008571, 0.002000, 0.032381],
    q25=[75.020000, 63.040000, 59.530000, 34.790000, 21.932857, 5.920000,
         0.820000, 0.180000, 0.040000, 0.040000, 0.010000, 0.000000,
         0.000000, 0.000000, 0.000000, 0.000000, 0.000000],
    q75=[94.560000, 72.280000, 77.240000, 50.205000, 47.432857, 6.490000,
         3.120000, 1.590000, 0.758333, 0.525000, 0.120000, 0.140000,
         0.000000, 0.000000, 0.010000, 0.000000, 0.000000],
)

# Reported scaling exponents (success ~ 2^{-b l}), from the cited article.
FIT_B = {"Direct": 1.0, "MC": 1.1, "CFA": 0.9}

METHODS = [
    ("Direct", DIRECT, BLUE, "o"),
    ("MC", MC, ORANGE, "s"),
    ("CFA", CFA, AQUA, "^"),
]


def fit_intercept(l, rate, b):
    l = np.asarray(l, dtype=float)
    rate = np.asarray(rate, dtype=float)
    mask = rate > 0
    y = np.log2(rate[mask] / 100.0) + b * l[mask]
    c = y.mean()
    return c


def percent_formatter():
    def fmt(y, _pos):
        return f"{y:g}\\%"
    return FuncFormatter(fmt)


def main():
    setup_style()
    fig, ax = plt.subplots(figsize=FIGSIZE)

    l_max = max(max(d["l"]) for _, d, _, _ in METHODS)
    l_grid = np.linspace(0, l_max, 200)

    for name, d, color, marker in METHODS:
        l = np.asarray(d["l"], dtype=float)
        rate = np.asarray(d["rate"], dtype=float)
        q25 = np.asarray(d["q25"], dtype=float)
        q75 = np.asarray(d["q75"], dtype=float)

        keep = rate > 0
        floor = 1e-3  # y-axis floor (in %), for whiskers that touch/exceed it
        lo = np.clip(np.minimum(q25, q75), floor, None)
        hi = np.clip(np.maximum(q25, q75), floor, None)

        for li, loi, hii in zip(l[keep], lo[keep], hi[keep]):
            ax.plot([li, li], [loi, hii], color=color, lw=1.0, alpha=0.6, zorder=2)

        ax.scatter(l[keep], rate[keep], color=color, marker=marker, s=16,
                   zorder=3, label=None, edgecolors="none")

        b = FIT_B[name]
        c = fit_intercept(l, rate, b)
        fit = 100.0 * 2.0 ** (c - b * l_grid)
        ax.plot(l_grid, fit, color=color, lw=1.2, zorder=1,
                 label=f"{name} Method $\\sim 2^{{-{b:.1f}\\,l}}$")

    ax.plot(l_grid, 100.0 * 2.0 ** (-l_grid), color=RED, lw=1.2,
            linestyle="--", zorder=1, label="Random $=2^{-1.0\\,l}$")

    ax.set_yscale("log")
    ax.set_xlim(0, l_max + 1)
    ax.set_ylim(1e-3, 200)
    ax.set_xlabel("Number of Unknown Bits $l=l_p^*+l_q^*$")
    ax.set_ylabel("Success Frequency")
    ax.yaxis.set_major_formatter(percent_formatter())
    style_legend(ax, loc="upper right")

    fig.tight_layout()
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(_OUT, bbox_inches="tight")
    print(f"Saved: {_OUT}")


if __name__ == "__main__":
    main()
