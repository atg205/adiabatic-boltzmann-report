#!/usr/bin/env python3
"""
T2 independent-evaluation arm, CPU only, on the one surviving N=32 QPU
checkpoint set (seed 94, iterations 0/20/40/60/80/99).

ClassicalSampler("gibbs") draws N_samples in PARALLEL independent chains
(each row of the (n_samples, N) batch is its own independently-initialized
and independently-evolved chain -- confirmed by reading _gibbs_sample in
src/sampler.py), not one long autocorrelated chain. So a bootstrap CI over
those i.i.d. parallel endpoints is valid directly, no autocorrelation
correction needed -- simpler than sequential-chain MCMC would require.

Mixing check: compare the independent-energy estimate at two different
warmup lengths (300 vs 600 sweeps); if they agree, 300 was enough.
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
CKPT_DIR = Path("/home/atg205/pipcache/claude-1001/-home-atg205-Documents-Dokumentte-Uni-UPMC-stage2gl-adiabatic-boltzmann-report/596b29cd-14b9-4083-9008-5ba72cf4273b/scratchpad/n32_seed94_checkpoints")
RESULT_FILE = ROOT / "results/tfim_1d/32/dimod/pegasus/result_1d_h0.5_rbmfull_nh32_lr0.08_reg0.05_ns200_seed94_iter100_cem1_sigma1.0.json.gz"
ITERS = [0, 20, 40, 60, 80, 99]
N_SAMPLES = 3000
EPSILON = 0.1
N_BOOT = 2000

ising = TransverseFieldIsing1D(N, H)

with gzip.open(RESULT_FILE) as f:
    result = json.load(f)
E0 = result["exact_energy"]
training_energy = result["history"]["energy"]  # per-iteration training-log energy


def load_ckpt(iteration):
    path = CKPT_DIR / f"checkpoint_1d_h0.5_rbmfull_nh32_lr0.08_iter{iteration:04d}.pkl"
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
    e_loc = np.asarray(ising.local_energy_batch(V, rbm))
    return e_loc


def bootstrap_ci(e_loc, n_boot=N_BOOT):
    n = len(e_loc)
    means = np.empty(n_boot)
    rng = np.random.default_rng(0)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        means[b] = e_loc[idx].mean()
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(e_loc.mean()), float(lo), float(hi), float(e_loc.var())


rows = []
for it in ITERS:
    rbm = load_ckpt(it)
    e_300 = independent_energy(rbm, 300, seed=10_000 + it)
    e_600 = independent_energy(rbm, 600, seed=20_000 + it)
    mean300 = e_300.mean(); mean600 = e_600.mean()
    mixing_gap = abs(mean300 - mean600)

    mean_i, lo_i, hi_i, var_i = bootstrap_ci(e_600)  # use the longer-warmup batch as final
    err_i = abs(mean_i - E0) / N
    err_hi = abs(hi_i - E0) / N if hi_i < E0 else abs(lo_i - E0) / N  # conservative upper bound on |err|
    err_hi = max(abs(lo_i - E0), abs(hi_i - E0)) / N

    train_e = training_energy[it]
    train_err = abs(train_e - E0) / N

    row = dict(iteration=it, E0=E0,
               independent_mean=mean_i, independent_ci=[lo_i, hi_i], independent_var=var_i,
               independent_err_per_spin=err_i, independent_err_upper_bound=err_hi,
               mixing_gap_300_vs_600=mixing_gap,
               training_log_energy=train_e, training_log_err_per_spin=train_err,
               validated_at_eps_0_1=bool(err_hi < EPSILON))
    rows.append(row)
    print(f"iter={it:3d}  training_log_err/spin={train_err:.4f}  "
          f"independent_err/spin={err_i:.4f} (CI upper {err_hi:.4f})  "
          f"mixing_gap={mixing_gap:.4f}  validated@0.1={err_hi < EPSILON}")

out = Path(__file__).resolve().parent / "t2_n32_seed94_independent_eval.json"
out.write_text(json.dumps(rows, indent=2))
print(f"\nsaved -> {out}")
