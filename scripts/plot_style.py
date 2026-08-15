"""Shared matplotlib style for the report's Fig. 1 panels (native TTS + factoring)."""
import matplotlib as mpl

FIGSIZE = (3.6, 3.2)

# Validated categorical palette (see dataviz skill / references/palette.md).
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
VIOLET = "#4a3aa7"
RED = "#e34948"


def setup_style(fontsize=9):
    mpl.rcParams.update({
        "pgf.texsystem": "pdflatex",
        "text.usetex": True,
        "font.family": "serif",
        "axes.labelsize": fontsize,
        "font.size": fontsize,
        "legend.fontsize": fontsize - 3,
        "xtick.labelsize": fontsize,
        "ytick.labelsize": fontsize,
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.2,
        "grid.linewidth": 0.5,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": True,
        "ytick.right": True,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "legend.frameon": True,
        "legend.framealpha": 1.0,
        "legend.fancybox": False,
        "legend.edgecolor": "black",
    })


def style_legend(ax, loc="upper right"):
    return ax.legend(loc=loc, handlelength=1.6, borderpad=0.4, labelspacing=0.4)
