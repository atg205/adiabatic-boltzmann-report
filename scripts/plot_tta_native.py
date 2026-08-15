#!/usr/bin/env python3
"""
Redraw of the native-formulation TTS99-vs-N panel (previously
figures/tta_overview_1.pdf) in the same style as plot_factoring_success.py,
so both panels of Fig. 1 share one look.

Data points and fitted-exponent beta values were recovered from the original
figure's vector PDF (marker path centers, calibrated against its axis tick
positions) since no source script/data table for it was found in the
adiabatic-boltzmann repo; the beta values match the ones printed in the
original legend exactly.

Usage:
    python scripts/plot_tta_native.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot_style import AQUA, BLUE, FIGSIZE, ORANGE, RED, VIOLET, YELLOW, setup_style, style_legend

_ROOT = Path(__file__).resolve().parent.parent
_OUT = _ROOT / "figures" / "tta_overview_native.pdf"

N_GRID = [16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112]

SOLVERS = [
    ("VeloxQ", 22.55, BLUE, "o",
     [1.20, 1.54, 2.34, 2.59, 2.99, 3.87, 5.58, 7.17, 10.83, 41.39, 39.90, 38.48, 86.18]),
    ("Advantage2 1.6", 16.81, ORANGE, "s",
     [807.97, 1259.12, 1705.95, 2431.09, 9326.89, 8232.88, 30803.05, 27155.93,
      41488.72, 45393.14, 52423.11, 111307.52, 420697.57]),
    ("Advantage 6.4", 11.18, AQUA, "^",
     [3841.23, 8515.04, 18138.84, 46028.01, 59811.34, 139674.60, 1430872.68,
      4195559.59, None, 8898356.75, 8969935.60, None, 4310689.73]),
    ("SA (CPU)", 29.84, YELLOW, "x",
     [1.66, 2.33, 2.99, 3.57, 4.26, 4.95, 5.67, 6.26, 6.91, 11.77, 31.78, 34.36, 55.81]),
    ("SA (GPU)", 33.02, VIOLET, "D",
     [6.59, 6.34, 12.82, 13.77, 16.30, 17.36, 24.10, 22.42, 28.66, 39.64, 73.39, 106.85, 142.47]),
]


def fit_intercept(n, tts, beta):
    n = np.asarray(n, dtype=float)
    tts = np.asarray(tts, dtype=float)
    y = np.log(tts) - n / beta
    return y.mean()


def main():
    setup_style()
    fig, ax = plt.subplots(figsize=FIGSIZE)

    n_grid = np.linspace(min(N_GRID), max(N_GRID), 200)

    for name, beta, color, marker, tts_vals in SOLVERS:
        n = np.array([ni for ni, t in zip(N_GRID, tts_vals) if t is not None], dtype=float)
        tts = np.array([t for t in tts_vals if t is not None], dtype=float)

        ax.scatter(n, tts, color=color, marker=marker, s=16, zorder=3,
                   label=None, edgecolors="none")

        c = fit_intercept(n, tts, beta)
        fit = np.exp(c + n_grid / beta)
        ax.plot(n_grid, fit, color=color, lw=1.2, zorder=1,
                 label=f"{name} ($\\beta={beta:.2f}$)")

    ax.set_yscale("log")
    ax.set_xlim(min(N_GRID) - 4, max(N_GRID) + 4)
    ax.set_xlabel("$N$")
    ax.set_ylabel("$\\mathrm{TTS}_{99}$ [ms]")
    style_legend(ax, loc="upper left")

    fig.tight_layout()
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(_OUT, bbox_inches="tight")
    print(f"Saved: {_OUT}")


if __name__ == "__main__":
    main()
