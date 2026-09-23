#!/usr/bin/env python3
"""
Numeric residual summary for the archived CEM (least-squares) vs. exact
ground-truth beta comparison. Pure reanalysis of an already-archived file
(plots/cem/cem_validation_results.json, 480 records, N in {8,12}, h in
{0.5,1,1.5,2}, checkpoint in {early,mid,late}, beta_x in {0.5,1,1.5,2},
5 seeds) -- no new sampling, no new experiments.

Closes the calibration.tex placeholder asking for numerical RMSE, bias,
relative error, and boundary-hit frequency instead of "very close."
"""
import json
from pathlib import Path

import numpy as np

REPO = Path("/home/atg205/Documents/Dokumentte/Uni/UPMC/stage2gl/adiabatic-boltzmann")
SRC = REPO / "plots" / "cem" / "cem_validation_results.json"
OUT = Path(__file__).resolve().parent

BOUND_LO, BOUND_HI = 0.01, 50.0
NEAR_LO, NEAR_HI = 0.02, 49.0  # "near boundary" thresholds


def main():
    d = json.loads(SRC.read_text())
    rows = []
    for ckpt in ("early", "mid", "late"):
        sub = [r for r in d if r["checkpoint"] == ckpt]
        gt = np.array([r["beta_ground_truth"] for r in sub])
        cem = np.array([r["beta_cem"] for r in sub])
        resid = cem - gt
        rel = np.abs(resid) / gt
        bhit = int(((cem < NEAR_LO) | (cem > NEAR_HI)).sum())
        rows.append(dict(
            checkpoint=ckpt, n=len(sub),
            bias=float(resid.mean()),
            rmse=float(np.sqrt((resid ** 2).mean())),
            median_rel_err=float(np.median(rel)),
            mean_rel_err=float(rel.mean()),
            boundary_hits=bhit,
            gt_min=float(gt.min()), gt_max=float(gt.max()),
        ))

    gt_all = np.array([r["beta_ground_truth"] for r in d])
    cem_all = np.array([r["beta_cem"] for r in d])
    resid_all = cem_all - gt_all
    rel_all = np.abs(resid_all) / gt_all
    bhit_all = int(((cem_all < NEAR_LO) | (cem_all > NEAR_HI)).sum())
    rows.append(dict(
        checkpoint="overall", n=len(d),
        bias=float(resid_all.mean()), rmse=float(np.sqrt((resid_all ** 2).mean())),
        median_rel_err=float(np.median(rel_all)), mean_rel_err=float(rel_all.mean()),
        boundary_hits=bhit_all,
        gt_min=float(gt_all.min()), gt_max=float(gt_all.max()),
    ))

    print(f"{'checkpoint':10s} {'n':>4s} {'bias':>8s} {'RMSE':>8s} {'med|rel|':>9s} {'mean|rel|':>10s} {'boundary-hit':>14s}")
    for r in rows:
        print(f"{r['checkpoint']:10s} {r['n']:4d} {r['bias']:+8.3f} {r['rmse']:8.3f} "
              f"{r['median_rel_err']:9.3f} {r['mean_rel_err']:10.3f} "
              f"{r['boundary_hits']:5d}/{r['n']} ({100*r['boundary_hits']/r['n']:.1f}%)")

    frac_gt_small = float((gt_all < 0.05).mean())
    print(f"\nFraction of records with ground-truth beta < 0.05: {frac_gt_small:.3f} "
          f"({int((gt_all<0.05).sum())}/{len(gt_all)}) -- this is why mean/median relative "
          f"error stays large (60-150%) even where bias/RMSE are small: dividing by a small "
          f"ground-truth beta inflates the ratio without reflecting poor absolute accuracy.")

    (OUT / "cem_residual_table.json").write_text(json.dumps(rows, indent=2))
    print("\nsaved cem_residual_table.json")


if __name__ == "__main__":
    main()
