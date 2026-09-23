#!/usr/bin/env python3
"""Minimal LIVE Pegasus draw at N=8 on an already-trained checkpoint, to
close the calibration.tex-flagged gap: a QPU DTV point on the same instance/
axes as fig:classical. Reuses the existing DimodSampler code path exactly --
no new sampler logic. Run from the repo root so time.json accounting matches
every other archived result.
"""
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp

sys.path.insert(0, "src")
from model import FullyConnectedRBM
from sampler import DimodSampler
from encoder import estimate_beta_eff_cem
from kl_utils import all_configs_jax, empirical_dist_jax

N = 8
CKPT = "checkpoints/cem_validation/tfim_N8_h1.0_late.pkl"

rbm = FullyConnectedRBM(N, N, jax.random.PRNGKey(0))
with open(CKPT, "rb") as f:
    d = pickle.load(f)
rbm.a = jnp.array(d["a"]); rbm.b = jnp.array(d["b"]); rbm.W = jnp.array(d["W"])

print("Connecting + drawing 200 live Pegasus samples at N=8 ...")
sampler = DimodSampler("pegasus")
BETA_X = 2.0  # max|W|~1.01 at beta_x=1.0 exceeded extended_j_range; safely inside at 2.0
v, h = sampler.sample(rbm, 200, config={"beta_x": BETA_X}, return_hidden=True)
print("Draw complete. embedding_info:", sampler.last_embedding_info)

V = jnp.asarray(v, dtype=jnp.float64)
H = jnp.asarray(h, dtype=jnp.float64)

# exact enumerated pi_theta
configs = all_configs_jax(N)
a_v = np.asarray(configs @ rbm.a)
theta_all = np.asarray(configs @ rbm.W + rbm.b[None, :])
log_psi2 = -a_v + np.sum(np.log(2 * np.cosh(theta_all)), axis=1)
log_psi2 -= log_psi2.max()
pi_exact = np.exp(log_psi2); pi_exact /= pi_exact.sum()

q_emp = np.asarray(empirical_dist_jax(V, N))
dtv = 0.5 * float(np.sum(np.abs(q_emp - pi_exact)))
beta_ls = estimate_beta_eff_cem(V, H, rbm)

result = {
    "N": N, "checkpoint": CKPT, "n_samples": 200,
    "dtv_vs_exact": dtv, "beta_ls": beta_ls,
    "embedding_info": sampler.last_embedding_info,
    "v_samples": np.asarray(v).tolist(),
    "h_samples": np.asarray(h).tolist(),
}
outpath = Path("/home/atg205/pipcache/claude-1001/-home-atg205-Documents-Dokumentte-Uni-UPMC-stage2gl-adiabatic-boltzmann-report/596b29cd-14b9-4083-9008-5ba72cf4273b/scratchpad/live_qpu_n8_result.json")
outpath.write_text(json.dumps(result, indent=2))

print(f"\nRESULT: D_TV(QPU, exact) = {dtv:.4f}")
print(f"RESULT: beta_LS (from live QPU samples) = {beta_ls:.4f}")
print(f"Saved raw samples + result -> {outpath}")
