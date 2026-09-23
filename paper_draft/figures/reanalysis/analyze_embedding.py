#!/usr/bin/env python3
"""
T5: QPU hardware-resource accounting, from the embedding_info field already
logged in archived result files (never extracted/reported before). Pure
reanalysis -- no new experiments, no new QPU/CPU time beyond reading JSON.
"""
import gzip
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

REPO = Path("/home/atg205/Documents/Dokumentte/Uni/UPMC/stage2gl/adiabatic-boltzmann")
OUT = Path(__file__).resolve().parent

mpl.rcParams.update({
    "font.size": 12, "axes.labelsize": 12, "axes.titlesize": 12,
    "legend.fontsize": 10, "xtick.labelsize": 10, "ytick.labelsize": 10,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
})
COLORS = {"pegasus": "#bc5090", "zephyr": "#ef5675"}
MARKERS = {"pegasus": "D", "zephyr": "h"}

SIZES = [8, 16, 32, 64]


SOLVER_NAME = {"pegasus": "Advantage_system6", "zephyr": "Advantage2_system1"}
DNX_SHAPE = {"pegasus": ("pegasus", (16,)), "zephyr": ("zephyr", (12, 4))}


def get_embedding_info(n, method):
    pat = str(REPO / f"results/tfim_1d/{n}/dimod/{method}/"
              f"result_1d_h0.5_rbmfull_nh{n}_lr0.08_reg0.05_ns200_seed0_iter100_cem1_sigma1.0.json.gz")
    import glob
    files = glob.glob(pat)
    if not files:
        return None
    with gzip.open(files[0]) as fh:
        d = json.load(fh)
    return d.get("embedding_info")


def recompute_embedding_offline(n, method):
    """N=16 is absent from every archived result file (checked multiple seeds).
    Recompute it offline from the cached LIVE hardware-graph snapshot used to
    generate every other size's embedding_info -- no QPU or network access,
    just minorminer.busclique against the same real (defect-aware) topology.
    """
    import dwave_networkx as dnx
    import minorminer.busclique as bc

    solver = SOLVER_NAME[method]
    hw_path = REPO / f"embeddings/_hwgraph_{solver}_live.json"
    if not hw_path.exists():
        return None
    d = json.loads(hw_path.read_text())
    node_list = [node for node, _ in d["nodes"]]
    edge_list = [tuple(e) for e in d["edges"]]
    topology, shape = DNX_SHAPE[method]
    gen = dnx.pegasus_graph if topology == "pegasus" else dnx.zephyr_graph
    g = gen(*shape, node_list=node_list, edge_list=edge_list, data=True)
    embedding = bc.busgraph_cache(g).find_biclique_embedding(n, n)
    if not embedding:
        return None
    chains = [len(v) for v in embedding.values()]
    return {"type": "biclique-offline", "solver": solver, "n_visible": n, "n_hidden": n,
            "max_chain": max(chains), "mean_chain": sum(chains) / len(chains), "qubits": sum(chains)}


def main():
    rows = []
    for method in ("pegasus", "zephyr"):
        for n in SIZES:
            info = get_embedding_info(n, method)
            source = "archived"
            if info is None:
                info = recompute_embedding_offline(n, method)
                source = "offline-recomputed" if info is not None else None
            if info is None:
                rows.append((method, n, None, None, None, None))
                continue
            rows.append((method, n, info["qubits"], info["mean_chain"], info["max_chain"], source))

    print(f"{'device':8s} {'N':>4s} {'qubits':>7s} {'logical':>8s} {'overhead':>9s} {'mean_chain':>11s} {'max_chain':>10s}  source")
    for method, n, qubits, mean_chain, max_chain, source in rows:
        logical = 2 * n  # N visible + N hidden (M=N in this study)
        if qubits is None:
            print(f"{method:8s} {n:4d} {'MISSING':>7s}")
            continue
        overhead = qubits / logical
        print(f"{method:8s} {n:4d} {qubits:7d} {logical:8d} {overhead:9.3f} {mean_chain:11.3f} {max_chain:10d}  {source}")

    # figure: qubits vs N and mean chain length vs N, log-log, both devices
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    for method in ("pegasus", "zephyr"):
        ns = [r[1] for r in rows if r[0] == method and r[2] is not None]
        qubits = [r[2] for r in rows if r[0] == method and r[2] is not None]
        chains = [r[3] for r in rows if r[0] == method and r[2] is not None]
        missing = [r[1] for r in rows if r[0] == method and r[2] is None]

        axes[0].plot(ns, qubits, marker=MARKERS[method], color=COLORS[method],
                     markersize=9, linewidth=1.8, label=f"{method.capitalize()}(+CEM)")
        axes[1].plot(ns, chains, marker=MARKERS[method], color=COLORS[method],
                     markersize=9, linewidth=1.8, label=f"{method.capitalize()}(+CEM)")
        for n_missing in missing:
            axes[0].axvline(n_missing, color=COLORS[method], linestyle=":", alpha=0.3)

    # reference line: qubits = 2N (no embedding overhead)
    ns_ref = np.array(SIZES)
    axes[0].plot(ns_ref, 2 * ns_ref, "k--", linewidth=1, alpha=0.6, label=r"$2N$ (no overhead)")

    axes[0].set_xscale("log"); axes[0].set_yscale("log")
    axes[0].set_xlabel("System size $N$"); axes[0].set_ylabel("Physical qubits used")
    axes[0].set_title("Physical qubits vs.\ $N$")
    axes[0].legend(fontsize=9)

    axes[1].set_xscale("log"); axes[1].set_yscale("log")
    axes[1].set_xlabel("System size $N$"); axes[1].set_ylabel("Mean chain length")
    axes[1].set_title("Mean chain length vs.\ $N$")
    axes[1].legend(fontsize=9)
    axes[1].text(0.05, 0.95, "$N=16$: recomputed offline\n(minorminer, cached live graph)",
                 transform=axes[1].transAxes, fontsize=8, va="top", color="#888888")

    fig.suptitle("QPU hardware-resource cost, from archived embedding\\_info (no new experiments)", fontsize=12.5)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_qpu_resource_scaling.{ext}")
    print("\nsaved fig_qpu_resource_scaling.pdf")


if __name__ == "__main__":
    main()
