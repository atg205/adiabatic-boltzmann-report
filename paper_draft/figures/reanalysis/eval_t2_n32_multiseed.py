#!/usr/bin/env python3
"""
T2 independent-evaluation arm, CPU only, now across all 5 N=32 QPU
checkpoint sets (seeds 90-94, iterations 0/20/40/60/80/99 each).

Same method as eval_t2_n32.py (parallel-chain Gibbs -> i.i.d. bootstrap CI,
mixing check via 300-vs-600-warmup agreement), just looped over seeds.
"""
import gzip
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp

ROOT = Path("/home/atg205/Documents/Dokumentte/Uni/UPMC/stage2gl/adiabatic-boltzmann")
sys.path.insert(0, str(ROOT / "src"))
from model import FullyConnectedRBM
from sampler import ClassicalSampler
from ising import TransverseFieldIsing1D

N = 32
H = 0.5
SCRATCH = Path("/home/atg205/pipcache/claude-1001/-home-atg205-Documents-Dokumentte-Uni-UPMC-stage2gl-adiabatic-boltzmann-report/596b29cd-14b9-4083-9008-5ba72cf4273b/scratchpad")
SEEDS = [90, 91, 92, 93, 94]
ITERS = [0, 20, 40, 60, 80, 99]
N_SAMPLES = 3000
EPSILON = 0.1
N_BOOT = 2000

ising = TransverseFieldIsing1D(N, H)


def load_ckpt(seed, iteration):
    path = SCRATCH / f"n32_seed{seed}_checkpoints" / f"checkpoint_1d_h0.5_rbmfull_nh32_lr0.08_iter{iteration:04d}.pkl"
    with open(path, "rb") as f:
        d = pickle.load(f)
    rbm = FullyConnectedRBM(N, N, jax.random.PRNGKey(0))
    rbm.a = jnp.array(d["rbm_state"]["a"])
    rbm.b = jnp.array(d["rbm_state"]["b"])
    rbm.W = jnp.array(d["rbm_state"]["W"])
    return rbm


def independent_energy(rbm, n_warmup, seed):
    sampler = ClassicalSampler("gibbs", n_warmup=n_warmup, n_sweeps=1)
    sampler._key = jax.random.PRNGKey(seed)
    v = sampler.sample(rbm, N_SAMPLES, config={"n_warmup": n_warmup, "n_sweeps": 1},
                        return_hidden=False, return_jax=True)
    V = jnp.asarray(v, dtype=jnp.float64)
    return np.asarray(ising.local_energy_batch(V, rbm))


def bootstrap_ci(e_loc, n_boot=N_BOOT):
    n = len(e_loc)
    means = np.empty(n_boot)
    rng = np.random.default_rng(0)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        means[b] = e_loc[idx].mean()
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(e_loc.mean()), float(lo), float(hi), float(e_loc.var())


all_rows = []
for seed in SEEDS:
    result_file = (ROOT / f"results/tfim_1d/32/dimod/pegasus/"
                   f"result_1d_h0.5_rbmfull_nh32_lr0.08_reg0.05_ns200_seed{seed}_iter100_cem1_sigma1.0.json.gz")
    with gzip.open(result_file) as f:
        result = json.load(f)
    E0 = result["exact_energy"]
    training_energy = result["history"]["energy"]

    for it in ITERS:
        rbm = load_ckpt(seed, it)
        e_300 = independent_energy(rbm, 300, seed=10_000 + seed * 1000 + it)
        e_600 = independent_energy(rbm, 600, seed=20_000 + seed * 1000 + it)
        mixing_gap = abs(e_300.mean() - e_600.mean())

        mean_i, lo_i, hi_i, var_i = bootstrap_ci(e_600)
        err_i = abs(mean_i - E0) / N
        err_hi = max(abs(lo_i - E0), abs(hi_i - E0)) / N

        train_e = training_energy[it]
        train_err = abs(train_e - E0) / N

        row = dict(seed=seed, iteration=it, E0=E0,
                   independent_mean=mean_i, independent_ci=[lo_i, hi_i],
                   independent_err_per_spin=err_i, independent_err_upper_bound=err_hi,
                   mixing_gap=mixing_gap,
                   training_log_energy=train_e, training_log_err_per_spin=train_err,
                   validated_at_eps_0_1=bool(err_hi < EPSILON))
        all_rows.append(row)
        agree = "AGREE" if (train_err < EPSILON) == (err_hi < EPSILON) else "*** DISAGREE ***"
        print(f"seed={seed} iter={it:3d}  train_err/spin={train_err:.4f}  "
              f"indep_err/spin={err_i:.4f} (CI_hi {err_hi:.4f})  mix_gap={mixing_gap:.4f}  {agree}")

out = SCRATCH / "t2_n32_multiseed_independent_eval.json"
out.write_text(json.dumps(all_rows, indent=2))
print(f"\nsaved -> {out}")

# Summary: how often does the training-log criterion disagree with the independent one?
disagreements = [r for r in all_rows
                 if (r["training_log_err_per_spin"] < EPSILON) != r["validated_at_eps_0_1"]]
print(f"\n{len(disagreements)}/{len(all_rows)} checkpoints where training-log and "
      f"independent verdicts disagree at eps=0.1:")
for r in disagreements:
    print(f"  seed={r['seed']} iter={r['iteration']}: "
          f"train_err={r['training_log_err_per_spin']:.4f} vs indep_CI_hi={r['independent_err_upper_bound']:.4f}")
