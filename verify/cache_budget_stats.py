#!/usr/bin/env python3
"""Finding C4: budget audit of the two arms behind Fig. 12b (report.tex L482-L501).

Fig. 12b (figures/sparsity/sparsity_ablation_qpu_vs_classical.pdf) plots relative
energy error vs. sparsity for two arms at N=16, h=1, Zephyr, alpha=1:

    classical MCMC arm -> figures/sparsity/cache_sparsity_ablation.json
    real-QPU arm       -> figures/sparsity/cache_sparsity_ablation_qpu.json

This script re-derives, from those committed caches alone, the per-(sparsity, seed)
SR iteration count and relative error of both arms, so that the training-budget
comparison in L482/L484 can be checked independently.

Cache layout (verified, not assumed -- the script re-checks it and reports it):

  * both files are flat dicts; the key encodes the run configuration as
        "<N>_<target_sparsity>_<h>_<graph>_<seed>"      e.g. "16_0.557_1.0_zephyr_42"
    NOTE: field 2 is the TARGET SPARSITY in these two files. In the other caches in
    the same directory (cache_full.json, cache_qpu_zephyr.json) field 2 is alpha
    instead, so keys are not interchangeable across files.
  * there is NO "seed" field and NO iteration-count field in the records. The seed is
    recoverable only from the key, and the realised SR iteration count only as
    len(energy_history). (An explicit "n_iters_run" field exists in exactly one record
    of cache_qpu_zephyr.json and nowhere else, so it cannot be used here.)
  * record fields: energy_history, E_exact, E_final, rel_error, n_params, sparsity
    (+ qpu_time_ms_used on the QPU arm only).
  * "sparsity" holds the REALISED sparsity, which differs from the rounded key label
    (key 0.877 -> realised 0.87890625).

Requires: standard library only (json). Deterministic; reads, never writes.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(HERE, os.pardir, "figures", "sparsity")

CLASSICAL = "cache_sparsity_ablation.json"
QPU = "cache_sparsity_ablation_qpu.json"

# Fig. 12b compares the two arms at h = 1 only; the classical cache also holds
# h in {0.3, 0.7, 1.3, 2.0}, which belong to Fig. 12a.
FIG12B_H = "1.0"


# --------------------------------------------------------------------------- io

def load(name):
    path = os.path.join(CACHE_DIR, name)
    if not os.path.exists(path):
        sys.exit("missing cache: %s" % path)
    with open(path) as fh:
        return json.load(fh)


def parse_key(key):
    """'16_0.557_1.0_zephyr_42' -> dict(N, sparsity_label, h, graph, seed)."""
    parts = key.split("_")
    if len(parts) != 5:
        return None
    return {
        "N": parts[0],
        "sparsity_label": parts[1],
        "h": parts[2],
        "graph": parts[3],
        "seed": parts[4],
    }


def n_iters(rec):
    """Realised SR iteration count = length of the recorded energy history."""
    hist = rec.get("energy_history")
    if not isinstance(hist, list):
        return None
    return len(hist)


# ------------------------------------------------------------------- statistics

def mean(xs):
    return sum(xs) / float(len(xs))


def collect(cache, arm, h_filter=None):
    """-> list of level dicts, ordered by realised sparsity."""
    groups = {}
    for key, rec in cache.items():
        meta = parse_key(key)
        if meta is None:
            continue
        if h_filter is not None and meta["h"] != h_filter:
            continue
        groups.setdefault(meta["sparsity_label"], []).append((meta, rec))

    levels = []
    for label, entries in groups.items():
        # order seeds by first appearance in the file, which is the run order
        entries.sort(key=lambda e: list(cache).index(
            "_".join([e[0]["N"], e[0]["sparsity_label"], e[0]["h"],
                      e[0]["graph"], e[0]["seed"]])))
        realised = sorted({r["sparsity"] for _, r in entries if "sparsity" in r})
        nparams = sorted({r["n_params"] for _, r in entries if "n_params" in r})
        iters = [n_iters(r) for _, r in entries]
        errs = [r["rel_error"] for _, r in entries]
        levels.append({
            "arm": arm,
            "label": label,
            "realised": realised,
            "n_params": nparams,
            "seeds": [m["seed"] for m, _ in entries],
            "iters": iters,
            "errs": errs,
            "qpu_ms": [r.get("qpu_time_ms_used") for _, r in entries],
        })
    levels.sort(key=lambda L: L["realised"][0] if L["realised"] else 0.0)
    return levels


def consistency_check(cache, name):
    """rel_error must equal |E_final - E_exact| / |E_exact| (i.e. NOT per spin)."""
    worst = 0.0
    tail = 0.0
    n_min_better = 0
    for rec in cache.values():
        if not all(k in rec for k in ("E_final", "E_exact", "rel_error")):
            continue
        want = abs(rec["E_final"] - rec["E_exact"]) / abs(rec["E_exact"])
        worst = max(worst, abs(want - rec["rel_error"]))
        hist = rec.get("energy_history")
        if isinstance(hist, list) and hist:
            tail = max(tail, abs(rec["E_final"] - hist[-1]) / abs(rec["E_exact"]))
            if abs(min(hist) - rec["E_exact"]) / abs(rec["E_exact"]) < rec["rel_error"]:
                n_min_better += 1
    print("  %s" % name)
    print("    max |rel_error - |dE|/|E_exact||        = %.3e"
          "   (0 => plain relative error, NOT per-spin)" % worst)
    print("    max |E_final - energy_history[-1]|/|E| = %.3e"
          "   (>0 => E_final is a fresh re-evaluation," % tail)
    print("                                                                 not the last "
          "history point)")
    print("    records where min(energy_history) < E_final: %d / %d"
          "   (rel_error uses E_final, the unbiased choice)"
          % (n_min_better, len(cache)))


# ---------------------------------------------------------------------- output

def print_structure(cla, qpu):
    print("=" * 108)
    print("CACHE STRUCTURE  (dir: figures/sparsity/)")
    print("=" * 108)
    for name, cache in ((CLASSICAL, cla), (QPU, qpu)):
        fields = sorted({f for rec in cache.values() for f in rec})
        hs = sorted({parse_key(k)["h"] for k in cache if parse_key(k)})
        labels = sorted({parse_key(k)["sparsity_label"] for k in cache if parse_key(k)})
        seeds = sorted({parse_key(k)["seed"] for k in cache if parse_key(k)}, key=int)
        print("  %s" % name)
        print("    records        : %d   (flat dict, key = N_targetSparsity_h_graph_seed)" % len(cache))
        print("    record fields  : %s" % ", ".join(fields))
        print("    h values       : %s" % ", ".join(hs))
        print("    sparsity labels: %s" % ", ".join(labels))
        print("    seed values    : %s   (in the KEY only; no 'seed' field exists)" % ", ".join(seeds))
        print("    iteration count: derived as len(energy_history); no n_iters field in this file")
    print()
    print("  consistency checks:")
    consistency_check(cla, CLASSICAL)
    consistency_check(qpu, QPU)
    print()


def print_table(levels):
    head = ("%-9s %-10s %-6s %-3s %-22s %19s %26s"
            % ("sparsity", "key label", "arm", "n", "seeds", "SR iters min/mean/max",
               "rel. error mean [min-max]"))
    print(head)
    print("-" * len(head))
    for L in levels:
        realised = ("%.8f" % L["realised"][0]) if len(L["realised"]) == 1 else str(L["realised"])
        it = [i for i in L["iters"] if i is not None]
        errs = L["errs"]
        print("%-9s %-10s %-6s %-3d %-22s %5d /%6.1f /%5d   %7.2f%% [%5.2f%% - %5.2f%%]"
              % (realised.rstrip("0").rstrip(".") if len(L["realised"]) == 1 else realised,
                 L["label"], L["arm"], len(L["seeds"]), ",".join(L["seeds"]),
                 min(it), mean(it), max(it),
                 100 * mean(errs), 100 * min(errs), 100 * max(errs)))
    print()


def print_per_seed(levels):
    head = ("%-12s %-6s %-6s %8s %12s %14s"
            % ("sparsity", "arm", "seed", "SR iters", "rel err [%]", "QPU ms"))
    print(head)
    print("-" * len(head))
    for L in levels:
        sp = "%.8f" % L["realised"][0] if len(L["realised"]) == 1 else "?"
        for seed, it, err, ms in zip(L["seeds"], L["iters"], L["errs"], L["qpu_ms"]):
            print("%-12s %-6s %-6s %8s %12.3f %14s"
                  % (sp, L["arm"], seed, it, 100 * err,
                     "-" if ms is None else "%.1f" % ms))
    print()


def print_claim_checks(cla_levels, qpu_levels):
    print("=" * 108)
    print("AUDIT CLAIM CHECKS (finding C4 and the withheld-QPU-numbers note)")
    print("=" * 108)

    cla_iters = [L["iters"] for L in cla_levels]
    qpu_iters = [L["iters"] for L in qpu_levels]
    qpu_errs = [L["errs"] for L in qpu_levels]

    uniform300 = all(i == 300 for lvl in cla_iters for i in lvl)
    print('  "classical arm ran a uniform 300 SR iterations at every sparsity level'
          ' and all 5 seeds"')
    print("      -> %s: classical counts = %s"
          % ("CONFIRMED" if uniform300 else "FALSE", cla_iters))
    print("         classical n seeds per level = %s" % [len(L["seeds"]) for L in cla_levels])

    flat = [i for lvl in qpu_iters for i in lvl]
    print('  "QPU arm ran 14-300"')
    print("      -> observed range %d-%d" % (min(flat), max(flat)))
    print('  "averaging ~27 iterations at the highest sparsity (0.879)"')
    top = qpu_levels[-1]
    print("      -> highest realised sparsity = %.8f, mean iters = %.1f"
          % (top["realised"][0], mean(top["iters"])))
    print('  "per-level QPU counts [31,300,205,176,26], [297,300,185,300,300],'
          ' [15,133,300,28,300], [44,25,18,14,32]"')
    print("      -> observed %s" % qpu_iters)

    print('  "QPU mean relative error is 8.4%, 9.6%, 35.8%, 59.9%"')
    print("      -> observed %s"
          % ["%.1f%%" % (100 * mean(e)) for e in qpu_errs])
    print('  "per-level seed ranges 0.7-16.8%, 4.3-20.2%, 8.0-69.6%, 34.4-87.4%"')
    print("      -> observed %s"
          % ["%.1f-%.1f%%" % (100 * min(e), 100 * max(e)) for e in qpu_errs])

    print('  report.tex L484: classical mean rel. error "rises from 10.5% to 22.3%"')
    print("      -> observed %s"
          % ["%.1f%%" % (100 * mean(L["errs"])) for L in cla_levels])

    print()
    print("  budget ratio (classical iters / QPU iters), per sparsity level:")
    for c, q in zip(cla_levels, qpu_levels):
        print("      sparsity %.8f : %6.1f / %6.1f = %5.2fx"
              % (c["realised"][0], mean(c["iters"]), mean(q["iters"]),
                 mean(c["iters"]) / mean(q["iters"])))
    print()
    print("  mask identity between the two arms (same subgraph per level?):")
    for c, q in zip(cla_levels, qpu_levels):
        same = (c["realised"] == q["realised"]) and (c["n_params"] == q["n_params"])
        print("      sparsity %.8f : realised %s vs %s, n_params %s vs %s -> %s"
              % (c["realised"][0], c["realised"], q["realised"],
                 c["n_params"], q["n_params"], "SAME" if same else "DIFFERENT"))
    print()
    print("  NOTE: no cache in figures/sparsity/ contains the exact-enumeration")
    print("  'ansatz floor' (report.tex L484, 1.1-1.8 percent); it is not")
    print("  reproducible from committed data.")
    print()


def main():
    cla = load(CLASSICAL)
    qpu = load(QPU)

    print_structure(cla, qpu)

    cla_levels = collect(cla, "class", h_filter=FIG12B_H)
    qpu_levels = collect(qpu, "QPU")

    print("=" * 108)
    print("FIG. 12b ARMS  (N=16, h=%s, zephyr, alpha=1)" % FIG12B_H)
    print("=" * 108)
    merged = []
    for c, q in zip(cla_levels, qpu_levels):
        merged.extend([c, q])
    print_table(merged)

    print("=" * 108)
    print("PER-SEED DETAIL")
    print("=" * 108)
    print_per_seed(merged)

    print("=" * 108)
    print("CLASSICAL CACHE, ALL h (Fig. 12a); h=%s is the Fig. 12b arm above" % FIG12B_H)
    print("=" * 108)
    hs = sorted({parse_key(k)["h"] for k in cla if parse_key(k)}, key=float)
    for h in hs:
        print("  h = %s" % h)
        for L in collect(cla, "class", h_filter=h):
            it = L["iters"]
            print("      sparsity %.8f  n_params %3d  n=%d seeds  iters %d/%.1f/%d"
                  "  rel err %6.2f%% [%5.2f%% - %5.2f%%]"
                  % (L["realised"][0], L["n_params"][0], len(L["seeds"]),
                     min(it), mean(it), max(it),
                     100 * mean(L["errs"]), 100 * min(L["errs"]), 100 * max(L["errs"])))
    print()

    print_claim_checks(cla_levels, qpu_levels)


if __name__ == "__main__":
    main()
