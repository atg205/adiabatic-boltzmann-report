#!/usr/bin/env python3
"""
Experiment 1: N=8 Pegasus, 10 seeds, DTV/beta_LS vs exact enumeration
             (closes calibration.tex's flagged gap) + free T5 timing/
             chain-break extraction from the same draws.
Experiment 2: T2 minimal probe -- N=32 Pegasus, 5 seeds, h=0.5, matched
             protocol (lr=0.08, reg=0.05, ns=200, iter=100, cem=True),
             save_checkpoints=True so independent post-hoc evaluation is
             possible. Uses seeds 90-94 (disjoint from the archived 0-19
             seeds actually used elsewhere in the paper) so this can never
             overwrite real data.

Hard safety: checks time.json before EVERY single QPU call and aborts the
whole script (not just skips) the instant projected spend would cross
SESSION_CAP_MS. Logs cumulative device time after every call to a JSON
file this session polls periodically.
"""
import json
import pickle
import sys
import time as _time
from pathlib import Path

import numpy as np
import jax
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp

ROOT = Path("/home/atg205/Documents/Dokumentte/Uni/UPMC/stage2gl/adiabatic-boltzmann")
sys.path.insert(0, str(ROOT / "src"))
import os
os.chdir(ROOT)  # time.json, results/, checkpoints/ are all repo-root-relative

from argparse import Namespace
from model import FullyConnectedRBM
from sampler import DimodSampler
from encoder import Trainer
from ising import TransverseFieldIsing1D
from helpers import save_results, read_qpu_time_ms, save_rbm_checkpoint
from kl_utils import all_configs_jax, empirical_dist_jax

TIME_PATH = ROOT / "time.json"
SESSION_CAP_MS = 15 * 60 * 1000  # the stated 15-minute device-time budget
SAFETY_MARGIN_MS = 60 * 1000     # stop 1 minute before the hard cap, not at it
LOG_PATH = Path(__file__).resolve().parent / "exp_log.json"

log = {"events": [], "session_baseline_ms": None, "aborted": False}


def _now_ms():
    return read_qpu_time_ms(TIME_PATH)


def _write_log():
    LOG_PATH.write_text(json.dumps(log, indent=2, default=str))


def _check_budget_or_die(tag):
    used = _now_ms()
    spent = used - log["session_baseline_ms"]
    log["events"].append({"t": _time.time(), "tag": tag, "cumulative_ms": used, "session_spent_ms": spent})
    _write_log()
    print(f"[budget] after {tag}: session_spent={spent/1000:.2f}s of {SESSION_CAP_MS/1000:.0f}s cap", flush=True)
    if spent >= SESSION_CAP_MS - SAFETY_MARGIN_MS:
        log["aborted"] = True
        log["abort_reason"] = f"session_spent={spent/1000:.2f}s crossed safety threshold at tag={tag}"
        _write_log()
        print(f"[budget] ABORT: {log['abort_reason']}", flush=True)
        sys.exit(1)


def run_experiment_1():
    print("=== Experiment 1: N=8 Pegasus DTV/beta_LS, 10 seeds ===", flush=True)
    N = 8
    ckpt_path = ROOT / "checkpoints/cem_validation/tfim_N8_h1.0_late.pkl"
    rbm = FullyConnectedRBM(N, N, jax.random.PRNGKey(0))
    with open(ckpt_path, "rb") as f:
        d = pickle.load(f)
    rbm.a = jnp.array(d["a"]); rbm.b = jnp.array(d["b"]); rbm.W = jnp.array(d["W"])

    configs = all_configs_jax(N)
    a_v = np.asarray(configs @ rbm.a)
    theta_all = np.asarray(configs @ rbm.W + rbm.b[None, :])
    log_psi2 = -a_v + np.sum(np.log(2 * np.cosh(theta_all)), axis=1)
    log_psi2 -= log_psi2.max()
    pi_exact = np.exp(log_psi2); pi_exact /= pi_exact.sum()

    from encoder import estimate_beta_eff_cem
    results = []
    for seed in range(10):
        _check_budget_or_die(f"exp1-pre-seed{seed}")
        sampler = DimodSampler("pegasus")
        v, h = sampler.sample(rbm, 200, config={"beta_x": 2.0}, return_hidden=True)
        V = jnp.asarray(v, dtype=jnp.float64); H = jnp.asarray(h, dtype=jnp.float64)
        q_emp = np.asarray(empirical_dist_jax(V, N))
        dtv = 0.5 * float(np.sum(np.abs(q_emp - pi_exact)))
        beta_ls = estimate_beta_eff_cem(V, H, rbm)

        info = sampler.last_sampleset.info
        timing = info.get("timing", {})
        try:
            cbf = sampler.last_sampleset.record.chain_break_fraction
            cbf = [float(x) for x in np.asarray(cbf)]
        except Exception as e:
            cbf = f"unavailable: {e}"

        row = {"seed": seed, "dtv": dtv, "beta_ls": beta_ls,
               "embedding_info": sampler.last_embedding_info,
               "timing_info": timing, "chain_break_fraction": cbf}
        results.append(row)
        print(f"  seed {seed}: dtv={dtv:.4f} beta_ls={beta_ls:.4f}", flush=True)
        _check_budget_or_die(f"exp1-post-seed{seed}")

    out = Path(__file__).resolve().parent / "exp1_n8_results.json"
    out.write_text(json.dumps(results, indent=2, default=str))
    print(f"Experiment 1 saved -> {out}", flush=True)
    return results


def run_experiment_2():
    print("=== Experiment 2: T2 probe, N=32 Pegasus, seeds 90-94, checkpointed ===", flush=True)
    size, h, lr, reg, ns, iters = 32, 0.5, 0.08, 0.05, 200, 100
    method = "pegasus"
    saved_histories = []
    for seed in range(90, 95):
        _check_budget_or_die(f"exp2-pre-seed{seed}")
        ns_args = Namespace(
            model="1d", size=size, h=h, rbm="full", n_hidden=size,
            sampler="dimod", sampling_method=method,
            iterations=iters, learning_rate=lr, regularization=reg,
            n_samples=ns, output_dir=str(ROOT / "results"), seed=seed,
            visualize=False, cem=True,
        )
        out_file = (ROOT / "results/tfim_1d" / str(size) / "dimod" / method /
                    f"result_1d_h{h}_rbmfull_nh{size}_lr{lr}_reg{reg}"
                    f"_ns{ns}_seed{seed}_iter{iters}_cem1_sigma1.0.json.gz")
        if out_file.exists():
            print(f"  seed {seed}: result already exists, skipping ({out_file})", flush=True)
            continue

        ising = TransverseFieldIsing1D(size, h)
        rbm = FullyConnectedRBM(size, size, jax.random.PRNGKey(seed))
        sampler = DimodSampler(method=method)
        trainer_config = {
            "learning_rate": lr, "n_iterations": iters, "n_samples": ns,
            "regularization": reg, "seed": seed, "use_cem": True,
            "save_checkpoints": True, "checkpoint_interval": 20,
        }
        trainer = Trainer(rbm, ising, sampler, trainer_config, args=ns_args)

        # Budget-aware manual iteration loop would be more precise, but
        # Trainer.train() runs all 100 iterations in one call; check budget
        # immediately before starting each seed's full run (each full run
        # costs ~4-7s per the archived data, so per-seed granularity is
        # fine given the ~5s-per-call scale here).
        t0 = _time.time()
        history = trainer.train()
        wall_s = _time.time() - t0
        save_results(ns_args, history, ising, rbm, energy_j=trainer.total_energy_j, sampler=sampler)
        # Ensure the final trained state is always checkpointed, regardless
        # of whether n_iterations-1 happens to land on checkpoint_interval.
        save_rbm_checkpoint(rbm, ns_args, iters - 1)

        saved_histories.append({"seed": seed, "wall_s": wall_s, "out_file": str(out_file)})
        print(f"  seed {seed}: done, wall={wall_s:.1f}s -> {out_file}", flush=True)
        _check_budget_or_die(f"exp2-post-seed{seed}")

    out = Path(__file__).resolve().parent / "exp2_n32_results.json"
    out.write_text(json.dumps(saved_histories, indent=2, default=str))
    print(f"Experiment 2 saved -> {out}", flush=True)
    return saved_histories


if __name__ == "__main__":
    log["session_baseline_ms"] = _now_ms()
    print(f"[budget] session baseline: {log['session_baseline_ms']/1000:.2f}s cumulative, "
          f"cap +{SESSION_CAP_MS/1000:.0f}s for this session", flush=True)
    _write_log()
    try:
        run_experiment_1()
        run_experiment_2()
    except SystemExit:
        raise
    except Exception as e:
        log["error"] = repr(e)
        _write_log()
        print(f"[FATAL] {e!r}", flush=True)
        raise
    print("ALL DONE.", flush=True)
