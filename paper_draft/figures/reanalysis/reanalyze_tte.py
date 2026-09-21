#!/usr/bin/env python3
"""
Reanalysis of archived TFIM h=0.5 result files using the fixed-cutoff-tau
approach discussed, replacing the buggy retry-formula TTE99.

READS ONLY already-archived result files from the adiabatic-boltzmann repo.
No new experiments, no modification of that repo.

Produces three figures:
  A) error-vs-time curves at N=64, all solvers, with eps reference lines
  B) T99(tau*) vs N, old (buggy) formula vs corrected fixed-cutoff formula
  C) Kaplan-Meier-style "still not converged" curves at N=64, with censoring
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

WINDOW = 10          # same causal rolling-mean window as the original TTE code
EPSILON = 0.1        # h=0.5 headline tolerance
P_TARGET = 0.99
N_BOOT = 500
RNG = np.random.default_rng(0)

# ---------------------------------------------------------------------------
# Paper-grade style
# ---------------------------------------------------------------------------
mpl.rcParams.update({
    "font.size": 12,
    "axes.labelsize": 12,
    "axes.titlesize": 12,
    "legend.fontsize": 9.5,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

COLORS = {
    "Metropolis": "#2a78d6",
    "Gibbs": "#008300",
    "Simulated Annealing": "#6a3d9a",
    "FPGA": "#ffa600",
    "Pegasus (+CEM)": "#bc5090",
    "Zephyr (+CEM)": "#ef5675",
}
MARKERS = {
    "Metropolis": "o", "Gibbs": "s", "Simulated Annealing": "v",
    "FPGA": "X", "Pegasus (+CEM)": "D", "Zephyr (+CEM)": "h",
}

CLASSICAL_SIZES = [8, 12, 16, 24, 32, 64]
HW_SIZES = [8, 16, 32, 64]


# ---------------------------------------------------------------------------
# Loading (mirrors scripts/viz/paper_figures.py's mcmc_recs/fpga_recs/dwave_recs)
# ---------------------------------------------------------------------------
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


def dwave_recs(method, n, cem=1):
    pat = (f"{REPO}/results/tfim_1d/{n}/dimod/{method}/"
           f"result_1d_h0.5_rbmfull_nh{n}_lr0.08_reg0.05_ns200_seed*_iter100_cem{cem}_sigma1.0.json.gz")
    return _matched(load(pat), n)


SOLVERS = [
    ("Metropolis", CLASSICAL_SIZES, lambda n: mcmc_recs("metropolis", n)),
    ("Gibbs", CLASSICAL_SIZES, lambda n: mcmc_recs("gibbs", n)),
    ("Simulated Annealing", CLASSICAL_SIZES, lambda n: mcmc_recs("simulated_annealing", n)),
    ("FPGA", HW_SIZES, lambda n: fpga_recs(n)),
    ("Pegasus (+CEM)", HW_SIZES, lambda n: dwave_recs("pegasus", n)),
    ("Zephyr (+CEM)", HW_SIZES, lambda n: dwave_recs("zephyr", n)),
]


# ---------------------------------------------------------------------------
# Per-seed trajectories
# ---------------------------------------------------------------------------
def error_trajectory(rec, window=WINDOW):
    energies = np.asarray(rec["history"]["energy"], dtype=float)
    exact = rec["exact_energy"]
    n = rec["config"]["size"]
    errs = np.empty(len(energies))
    csum = np.cumsum(energies)
    csum = np.insert(csum, 0, 0.0)
    for t in range(len(energies)):
        w_start = max(0, t - window + 1)
        mean_e = (csum[t + 1] - csum[w_start]) / (t - w_start + 1)
        errs[t] = abs(mean_e - exact) / n
    return errs


def cum_time(rec):
    hist = rec["history"]
    key = "total_sampling_time_s" if "total_sampling_time_s" in hist else "sampling_time_s"
    return np.cumsum(np.asarray(hist[key], dtype=float))


def compute_validated_convergence_iter(errors, epsilon, window=WINDOW):
    n = len(errors)
    for t in range(n):
        if errors[t] < epsilon:
            end = t + window
            if end <= n and np.all(errors[t:end] < epsilon):
                return t  # 0-indexed here
    return None


def error_at_time(ct, errs, tau):
    idx = np.searchsorted(ct, tau, side="right") - 1
    if idx < 0:
        return np.inf
    return errs[idx]


# ---------------------------------------------------------------------------
# Old (buggy) TTE99, exactly reproducing paper_figures.py's formula
# ---------------------------------------------------------------------------
def median_iqr(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None, None, None
    return (float(np.percentile(vals, 50)), float(np.percentile(vals, 25)), float(np.percentile(vals, 75)))


def old_tte99(recs, epsilon=EPSILON, p_target=P_TARGET):
    ttes = []
    for r in recs:
        errs = error_trajectory(r)
        it = compute_validated_convergence_iter(errs, epsilon)
        if it is not None:
            ttes.append(float(cum_time(r)[it]))
    p = len(ttes) / len(recs) if recs else 0.0
    if not ttes:
        return None, p
    m, lo, hi = median_iqr(ttes)
    if p >= 1.0:
        return m, p
    R = np.log(1 - p_target) / np.log(1 - p)
    return m * R, p


# ---------------------------------------------------------------------------
# Fixed-cutoff (corrected) TTE99*
# ---------------------------------------------------------------------------
def p_of_tau(errs_list, ct_list, tau, epsilon):
    hits = sum(1 for errs, ct in zip(errs_list, ct_list) if error_at_time(ct, errs, tau) < epsilon)
    return hits / len(errs_list)


def t99_curve(recs, epsilon=EPSILON, p_target=P_TARGET, n_tau=60):
    errs_list = [error_trajectory(r) for r in recs]
    ct_list = [cum_time(r) for r in recs]
    tau_min = min(ct[0] for ct in ct_list)
    tau_max = max(ct[-1] for ct in ct_list)
    taus = np.geomspace(tau_min, tau_max, n_tau)
    ps = np.array([p_of_tau(errs_list, ct_list, tau, epsilon) for tau in taus])
    t99 = np.full_like(taus, np.inf)
    ok = ps > 0
    t99[ok & (ps >= 1.0)] = taus[ok & (ps >= 1.0)]
    mid = ok & (ps > 0) & (ps < 1.0)
    t99[mid] = taus[mid] * np.log(1 - p_target) / np.log(1 - ps[mid])
    return taus, ps, t99, errs_list, ct_list


def corrected_tte99(recs, epsilon=EPSILON, p_target=P_TARGET, n_boot=N_BOOT):
    if not recs:
        return None, None, None
    taus, ps, t99, errs_list, ct_list = t99_curve(recs, epsilon, p_target)
    if not np.any(np.isfinite(t99)):
        return None, None, None
    i_star = np.nanargmin(t99)
    point = t99[i_star]
    tau_star = taus[i_star]
    # bootstrap CI on the minimized T99 (resample seeds with replacement)
    n = len(recs)
    boot_vals = []
    for _ in range(n_boot):
        idx = RNG.integers(0, n, n)
        e_b = [errs_list[i] for i in idx]
        c_b = [ct_list[i] for i in idx]
        ps_b = np.array([p_of_tau(e_b, c_b, tau, epsilon) for tau in taus])
        t99_b = np.full_like(taus, np.inf)
        ok = ps_b > 0
        t99_b[ok & (ps_b >= 1.0)] = taus[ok & (ps_b >= 1.0)]
        mid = ok & (ps_b > 0) & (ps_b < 1.0)
        t99_b[mid] = taus[mid] * np.log(1 - p_target) / np.log(1 - ps_b[mid])
        if np.any(np.isfinite(t99_b)):
            boot_vals.append(np.nanmin(t99_b))
    if boot_vals:
        lo, hi = np.percentile(boot_vals, [2.5, 97.5])
    else:
        lo, hi = point, point
    return point, lo, hi


# ---------------------------------------------------------------------------
# Figure A: error-vs-time curves at N=64
# ---------------------------------------------------------------------------
def figure_a(n_focus=64):
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    for label, sizes, getter in SOLVERS:
        if n_focus not in sizes:
            continue
        recs = getter(n_focus)
        if not recs:
            continue
        errs_list = [error_trajectory(r) for r in recs]
        ct_list = [cum_time(r) for r in recs]
        tau_min = min(ct[0] for ct in ct_list)
        tau_max = max(ct[-1] for ct in ct_list)
        taus = np.geomspace(tau_min, tau_max, 60)
        med, lo, hi = [], [], []
        for tau in taus:
            vals = [error_at_time(ct, errs, tau) for ct, errs in zip(ct_list, errs_list)]
            vals = [v for v in vals if np.isfinite(v)]
            if not vals:
                med.append(np.nan); lo.append(np.nan); hi.append(np.nan)
                continue
            med.append(np.percentile(vals, 50))
            lo.append(np.percentile(vals, 25))
            hi.append(np.percentile(vals, 75))
        med, lo, hi = np.array(med), np.array(lo), np.array(hi)
        ax.plot(taus, med, color=COLORS[label], marker=MARKERS[label], markevery=8,
                markersize=6, linewidth=1.8, label=f"{label} ({len(recs)} seeds)")
        ax.fill_between(taus, lo, hi, color=COLORS[label], alpha=0.15, linewidth=0)

    for eps, style, lw in [(0.1, "-", 1.4), (0.05, "--", 1.0), (0.02, ":", 1.0), (0.01, "-.", 1.0)]:
        ax.axhline(eps, color="#444444", linestyle=style, linewidth=lw, alpha=0.7)
        ax.annotate(rf"$\epsilon={eps:g}$", xy=(tau_max, eps), xytext=(2, 2),
                    textcoords="offset points", fontsize=8.5, color="#444444", ha="left")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Cumulative sampling time [s]")
    ax.set_ylabel(r"Achieved energy error per spin  $|\overline{E}_t - E_0|/N$")
    ax.set_title(f"Error-vs-time, $N={n_focus}$, $h=0.5$ (median, IQR band)")
    ax.legend(loc="upper right", frameon=True, framealpha=0.9)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig_error_vs_time_N{n_focus}.{ext}"))
    plt.close(fig)
    print(f"[A] saved fig_error_vs_time_N{n_focus}.pdf")


# ---------------------------------------------------------------------------
# Figure A-grid: error-vs-time small multiples, one panel per N
# ---------------------------------------------------------------------------
def figure_a_grid(sizes=CLASSICAL_SIZES, ncols=None):
    if ncols is None:
        ncols = 2 if len(sizes) <= 4 else 3
    nrows = int(np.ceil(len(sizes) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5.0 * ncols, 4.2 * nrows), sharey=True)
    axes = np.atleast_1d(axes).ravel()

    for ax, n_focus in zip(axes, sizes):
        any_series = False
        tau_max_global = 0.0
        for label, sizes_avail, getter in SOLVERS:
            if n_focus not in sizes_avail:
                continue
            recs = getter(n_focus)
            if not recs:
                continue
            any_series = True
            errs_list = [error_trajectory(r) for r in recs]
            ct_list = [cum_time(r) for r in recs]
            tau_min = min(ct[0] for ct in ct_list)
            tau_max = max(ct[-1] for ct in ct_list)
            tau_max_global = max(tau_max_global, tau_max)
            taus = np.geomspace(tau_min, tau_max, 50)
            med, lo, hi = [], [], []
            for tau in taus:
                vals = [error_at_time(ct, errs, tau) for ct, errs in zip(ct_list, errs_list)]
                vals = [v for v in vals if np.isfinite(v)]
                if not vals:
                    med.append(np.nan); lo.append(np.nan); hi.append(np.nan)
                    continue
                med.append(np.percentile(vals, 50))
                lo.append(np.percentile(vals, 25))
                hi.append(np.percentile(vals, 75))
            med, lo, hi = np.array(med), np.array(lo), np.array(hi)
            ax.plot(taus, med, color=COLORS[label], marker=MARKERS[label], markevery=10,
                    markersize=5, linewidth=1.6, label=label)
            ax.fill_between(taus, lo, hi, color=COLORS[label], alpha=0.13, linewidth=0)

        if any_series:
            ax.axhline(EPSILON, color="#444444", linestyle="-", linewidth=1.1, alpha=0.7)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(f"$N={n_focus}$", fontsize=12)
        ax.set_xlabel("Cumulative sampling time [s]")

    for ax in axes[len(sizes):]:
        ax.axis("off")
    for i, ax in enumerate(axes[:len(sizes)]):
        if i % ncols == 0:
            ax.set_ylabel(r"Error per spin $|\overline{E}_t-E_0|/N$")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=6, fontsize=9.5,
               bbox_to_anchor=(0.5, 1.04), frameon=False)
    fig.suptitle(rf"Error-vs-time across $N$, $h=0.5$ (median, IQR band; solid line = $\epsilon={EPSILON:g}$)",
                 fontsize=13, y=1.09)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig_error_vs_time_grid.{ext}"))
    plt.close(fig)
    print("[A-grid] saved fig_error_vs_time_grid.pdf")


# ---------------------------------------------------------------------------
# Figure B: T99(tau*) vs N, old vs corrected
# ---------------------------------------------------------------------------
def figure_b():
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2), sharey=True)
    summary_rows = []
    for label, sizes, getter in SOLVERS:
        xs_old, ys_old = [], []
        xs_new, ys_new, lo_new, hi_new = [], [], [], []
        for n in sizes:
            recs = getter(n)
            if not recs:
                continue
            m_old, p_old = old_tte99(recs)
            if m_old is not None:
                xs_old.append(n); ys_old.append(m_old)
            m_new, lo, hi = corrected_tte99(recs)
            if m_new is not None:
                xs_new.append(n); ys_new.append(m_new); lo_new.append(lo); hi_new.append(hi)
            summary_rows.append((label, n, len(recs), p_old, m_old, m_new, lo, hi))
        axes[0].plot(xs_old, ys_old, color=COLORS[label], marker=MARKERS[label],
                     markersize=8, linewidth=1.8, linestyle="--", label=label)
        if xs_new:
            yerr = [[y - l for y, l in zip(ys_new, lo_new)], [h - y for y, h in zip(ys_new, hi_new)]]
            axes[1].errorbar(xs_new, ys_new, yerr=yerr, color=COLORS[label], marker=MARKERS[label],
                              markersize=8, linewidth=1.8, capsize=4, label=label)

    axes[0].set_title(r"Original: $T_r\cdot\ln(0.01)/\ln(1-p)$" + "\n(retry charged at successful-seed cost)")
    axes[1].set_title(r"Corrected: $\min_\tau\ \tau\ln(0.01)/\ln(1-p_\tau)$" + "\n(retry charged at fixed cutoff $\\tau$, bootstrap 95% CI)")
    for ax in axes:
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xticks(CLASSICAL_SIZES)
        ax.set_xticklabels([str(n) for n in CLASSICAL_SIZES])
        ax.minorticks_off()
        ax.set_xlabel("System size $N$")
    axes[0].set_ylabel(r"TTE$_{99}$ to $\epsilon=0.1$ [s]")
    axes[1].legend(loc="upper left", fontsize=8.5, framealpha=0.9)
    fig.suptitle(r"$h=0.5$, $\epsilon=0.1$: effect of correcting the retry-cost model", fontsize=13)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig_tte99_old_vs_corrected.{ext}"))
    plt.close(fig)
    print("[B] saved fig_tte99_old_vs_corrected.pdf")

    # dump the underlying numbers so they can be sanity-checked / cited
    with open(os.path.join(OUT, "tte99_reanalysis_table.csv"), "w") as fh:
        fh.write("solver,N,n_seeds,p_old(eps=0.1),TTE99_old[s],TTE99_corrected[s],CI_lo,CI_hi\n")
        for row in summary_rows:
            label, n, ns, p_old, m_old, m_new, lo, hi = row
            fh.write(f"{label},{n},{ns},{p_old:.3f},"
                     f"{'' if m_old is None else f'{m_old:.4g}'},"
                     f"{'' if m_new is None else f'{m_new:.4g}'},"
                     f"{'' if lo is None else f'{lo:.4g}'},"
                     f"{'' if hi is None else f'{hi:.4g}'}\n")
    print("[B] saved tte99_reanalysis_table.csv")


# ---------------------------------------------------------------------------
# Figure C: "fraction not yet converged" (1 - empirical CDF) at N=64, with
# censoring ticks -- a simple Kaplan-Meier-style plot (no ties handling
# beyond what np.unique gives us, which is fine at n=20).
# ---------------------------------------------------------------------------
def km_curve(times, censored):
    times = np.asarray(times, dtype=float)
    censored = np.asarray(censored, dtype=bool)
    order = np.argsort(times)
    times, censored = times[order], censored[order]
    n_at_risk = len(times)
    s = 1.0
    xs, ys = [0.0], [1.0]
    cens_x = []
    i = 0
    while i < len(times):
        t = times[i]
        j = i
        d = 0
        while j < len(times) and times[j] == t:
            if not censored[j]:
                d += 1
            else:
                cens_x.append(t)
            j += 1
        if d > 0:
            s *= (1 - d / n_at_risk)
            xs.append(t); ys.append(s)
        n_at_risk -= (j - i)
        i = j
    return np.array(xs), np.array(ys), np.array(cens_x)


def figure_c(n_focus=64, epsilon=EPSILON):
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    for label, sizes, getter in SOLVERS:
        if n_focus not in sizes:
            continue
        recs = getter(n_focus)
        if not recs:
            continue
        times, censored = [], []
        for r in recs:
            errs = error_trajectory(r)
            it = compute_validated_convergence_iter(errs, epsilon)
            ct = cum_time(r)
            if it is not None:
                times.append(ct[it]); censored.append(False)
            else:
                times.append(ct[-1]); censored.append(True)
        xs, ys, cens_x = km_curve(times, censored)
        ax.step(xs, ys, where="post", color=COLORS[label], linewidth=1.8,
                 label=f"{label} ({sum(censored)}/{len(recs)} censored)")
        cens_y = [ys[np.searchsorted(xs, cx, side="right") - 1] for cx in cens_x]
        ax.scatter(cens_x, cens_y, marker="|", color=COLORS[label], s=80, zorder=5)
    ax.set_xscale("log")
    ax.set_xlabel("Cumulative sampling time [s]")
    ax.set_ylabel(r"$S(t)=$ fraction not yet converged ($\epsilon=0.1$)")
    ax.set_title(f"Kaplan–Meier convergence curves, $N={n_focus}$, $h=0.5$\n(tick = censored seed, i.e. did not converge in budget)")
    ax.set_ylim(-0.03, 1.03)
    ax.legend(loc="lower left", fontsize=8.5, framealpha=0.9)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"fig_km_convergence_N{n_focus}.{ext}"))
    plt.close(fig)
    print(f"[C] saved fig_km_convergence_N{n_focus}.pdf")


if __name__ == "__main__":
    figure_a_grid(sizes=HW_SIZES, ncols=4)
