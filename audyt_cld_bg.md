# Audit: *Quantum Variational Algorithms on Adiabatic Quantum Computing Devices* (`report.tex`)

**Revision 11** — 2026-08-25. A verification pass, not a new audit. Every finding of revisions 8–10 was re-checked against the current manuscript; **the closed ones have been deleted from this document** and survive only as the one-line record in §3, so what remains below is the open list and nothing else.

*Provenance of this document.* Revision 8 was a full eight-lens re-audit. Revision 9 corrected three errors of revision 8 that had reached a published state — a stale `auto_scale` blocker, a reproducibility verdict formed from an out-of-date checkout, and several "missing" items that were in fact present. Revision 10 corrected revision 9 after a second review round: it rewrote the clock finding on verified implementation code, downgraded the scaling claim from proven artefact to confounded, withdrew a sub-finding, and refuted — with the indexing arithmetic — a proposed blocker about a supposedly forward-looking validation window. Each correction is recorded in the finding it touches. The separate changelog and review files have been removed at the author's request; this file is now the whole audit.

**Target.** `report.tex` at **`9917b34`** ("small text fixes") — 796 lines, 27 compiled pages. Bibliography: 29 entries. Verify with `wc -l report.tex` (→ 796) and `git log -1 --format=%h -- report.tex` (→ `9917b34`). Implementation repository: `iitis/adiabatic-boltzmann`, last inspected at `a4b0f2006`.

**Verdict of this pass: 16 of 24 findings are verified closed, 8 remain.** The three post-audit commits (`5ab5210` "fixed audits findings", `a8d03fc`, `9917b34`) resolved every blocking finding except one, and did so properly rather than cosmetically — the fixes were checked against the text, not taken from the changelog. What is left is one substantive contradiction, one missing experiment, and six items of provenance and polish.

---

## 0. Exposure status — still not fully closed

The private bank document is gone from the rewritten history: `git log --all` and `git rev-list --objects --all` find zero references to the path or blob, and the local clone has been reset onto the rewritten history and garbage-collected, so it is clean here too. *(confirmed)*

**But the force-push did not delete the dangling objects on GitHub.** Pre-rewrite commit SHAs remain browsable by direct URL until GitHub garbage-collects them. Two steps remain, both needing repo-owner credentials:

1. Make the repository private as an immediate stop-gap — this blocks anonymous access to every URL including dangling commits.
2. File a GitHub Support request to purge the cached objects, citing the repository, the path `figures/2_5316856890368498963.pdf`, and every pre-rewrite SHA that touched it.

Until step 2 is confirmed, treat the file as reachable by anyone holding an old SHA. The file itself still sits untracked and `.gitignore`d in `figures/` on disk — it is yours to keep or delete, but it does not belong in a project folder.

**Resolved 2026-08-25:** the changelog, the three review documents, the `verify/*.py` scaffolding and a tracked `__pycache__` artefact have been removed from the repository, so this file is the only audit material that ships with it.

---

## 1. Open findings

### O1 — "Only on classical hardware" is still contradicted by this repository's own data *(confirmed)*

L485: "Due to budget constraints, we tested the sparse models only on classical hardware." Still present, and `figures/sparsity/cache_sparsity_ablation_qpu.json` is **still tracked here** — 20 real QPU training runs on exactly those four masks, N=16, Zephyr, seeds 42/123/456/789/1234, each with a populated `qpu_time_ms_used`. The misleadingly named `sparsity_ablation_qpu_vs_classical.pdf` and `sparsity_heatmap_REAL_QPU_zephyr.pdf` are also still tracked.

The audit trail says the cache was deleted upstream on 2026-08-19; whether or not that happened in the implementation repository, it is still here, so a reader still finds data that refutes the sentence.

Restoring the arm is not clean — the QPU runs used 14–300 SR iterations against a uniform 300 classically. **Fix:** either say what was actually run ("a real-QPU arm was run but is not reported because its iteration budget was not matched to the classical arms"), or remove the cache and the two QPU-named figures from this repository so text and data agree. Rename the figure file either way.

### O2 — No QPU sampling-quality measurement *(confirmed)*

The Sampling Quality section (L281–320) contains **zero** mentions of the QPU or D-Wave; no QPU `D_TV` number appears in the prose anywhere. The only QPU distribution-quality data in the document remains the auto-scale ablation, run at different sample counts and floors, so it cannot be read against the classical benchmark. CEM is deployed on QPU samples but never validated on them, and no β_eff is reported for any QPU run that uses it. This is the paper's original stated aim and the largest remaining gap in substance. **Fix:** add a QPU `D_TV` curve at N=8 against the enumerable exact distribution, on the same axes as the classical benchmark.

### O3 — ε-sensitivity of the headline result is undisclosed *(confirmed; flagged as deferred by the author)*

ε=0.1 is stated (L556, L715) and the figure filenames are now parameterised, so the artefact is traceable — that part is fixed. What remains is that the conclusion's ε-dependence is not shown, and the author's own note records that Zephyr(+CEM)'s fitted exponent **changes sign between ε=0.10 and ε=0.15**. A scaling claim whose sign depends on an undisclosed threshold choice needs the sensitivity table. **Fix:** report validated counts, medians and exponents for at least ε ∈ {0.01, 0.1}, and say which the paper reports and why.

### O4 — Figure 1(a)'s data provenance is undisclosed *(confirmed)*

Its points were recovered from the published figure's vector paths rather than from underlying data — the generating script says so, the caption does not. `grep` for "recovered from", "digitis", "re-extracted" in `report.tex` returns nothing. **Fix:** one clause in the caption.

### O5 — The availability statement names no commit *(confirmed)*

L717 gives the repository URL with no commit hash or DOI, for a repository that moved 13 commits between the two states this audit pinned and 82 since the checkout it was first judged from. QPU access dates are now recorded (2026-05-11 to 2026-08-10) — that half is fixed — but library versions remain unpinned. **Fix:** pin a commit hash or mint a Zenodo DOI, and pin versions in `requirements.txt`.

### O6 — One bibliography record still incomplete *(confirmed)*

`Mehta_2025` still prints with volume and issue but no page or article number; the article number is **032616**. The other three record errors flagged earlier are fixed: the VeloxQ author list no longer names the replaced author, `willsch2024state` now carries its NIC Series 2025 publication, and `rrf3-jm5m` uses `number`. **Fix:** add `pages={032616}`.

### O7 — LaTeX structure *(confirmed)*

No `\appendix`, so the appendix prints as a numbered section with equation numbering running on; no `\date{}`, so the title page stamps the build date and changes on every rebuild. `\hypersetup` and `\lstset` are now present — those halves are fixed. **Fix:** two lines.

### O8 — The two sampler clocks' boundaries are not stated side by side *(minor, residual)*

The axis is now honestly labelled sampler time, excluding SR/CG/gradient work "which is identical across solvers" (L556) — the substantive half of this finding is fixed. The residual is that the QPU number is device-reported `qpu_access_time` (programming, anneal, readout, excluding queue and network) while the classical number is host wall-clock around the sampler call; the caption's "absolute scale stays directly comparable" (L560) does not distinguish them. **Fix:** one sentence naming both boundaries.

---

## 2. Priorities

1. **O1** — the only remaining contradiction between the text and committed data, and the largest credibility risk.
2. **O2** — the paper's stated aim; needs an experiment, not an edit.
3. **O3** — a sign-flipping exponent behind an undisclosed threshold.
4. **O4, O5, O6, O7, O8** — all single edits, an hour together.
5. §0 steps 1–2 — outside the manuscript, but the clock is running.

---

## 3. Closed in this pass — record only

Verified against the current text, not taken from the changelog. Each was a blocking (B) or major (M) finding in revisions 8–10.

| Was | Finding | How it was closed |
|---|---|---|
| B1 | Headline scaling claim confounded by a size-dependent CV stopping rule | The CV self-detector is gone entirely; TTE is now a plain sustained rolling-window crossing. `grep` for "coefficient of variation" → 0. |
| B2 | Axis labelled wall-clock training time while plotting sampler time | L556 now says "sampler time (the sampling call itself, excluding SR/CG/gradient work, which is identical across solvers)". Residual → **O8**. |
| B3 | Solver-ordering sentence false against its own figure | "consistently fastest" and "both QPUs overtake" both removed. |
| B4 | Abstract and Conclusion overclaimed a strict FPGA win | "at every size tested" and "classical and quantum alike" both removed. |
| B6 | Average sign identically zero for the models it characterised | ⟨s⟩ is now defined on the Marshall-transformed amplitude φ, and L522 states explicitly that on the untransformed Ψ₀ it "is identically zero for any singlet ground state by SU(2) symmetry". The with/without-Marshall ablation figure is included. |
| B7 | Two citations did not support their claims | The Heisenberg model now cites `Heisenberg_1928`; the lecture note moved to the TFIM sentence where it is correct. SR now cites `{Sorella_1998,Sorella_2001}`. |
| B8 | Shipped figure not producible from committed code | Figure filenames are parameterised again (`…_validated_convergence_eps0.1.pdf`). Residual → **O3**. |
| M1 | Energy caption claimed "the same validated-convergence cells" | Claim removed. |
| M2 | Fig. 4(a) caption wrong by a factor of two (24 vs 12 units) | Caption corrected. |
| M3 | Hardware paragraph contradicted itself about simulated annealing | Now states SA runs on the JAX/GPU path and that "a separate `dwave-neal`-based SA implementation also exists in the codebase but is not used for any result in this paper". |
| M4 | Benchmark did not state its problem | L558 now gives the hidden-unit count ("N hidden units, matching the visible count") alongside the TFIM, h=0.5, seeds and protocol. |
| M5 | Coverage-gap sentence | Removed. |
| M6 | Sparsity floor shape and the "8–17×" band | Disputed phrasings all removed. |
| M8 | Parallel-embedding numbers misdescribed | L487 now states the values are "each run's total recorded QPU time over its full 150-iteration budget, not the time at which it actually reached the energy plateau", and discloses that 2 of 3 seeds diverged. |
| M10 | Thirteen sections uncited; foundational references absent | Bibliography went from 16 to **29** entries, adding `Carleo_2017`, `King_2025`, `Goto_2019`, `Marshall_1955`, `Metropolis_1953`, `Hastings_1970`, `Kirkpatrick_1983`, `Geman_1984`, `Benedetti_2016`, `Pelofske_2022`, `Sorella_1998`, `Heisenberg_1928`, `Voigt_2000`. |
| M13 | Seeding protocol non-reproducible and contradicted by the caches | `np.random.randint` sentence removed; seeds stated. |
| M16 | `auto_scale` causal claim was a temperature confound | "dramatically worsens sampling performance" removed. |

*Not re-verified at pixel level:* M7 (legend occluding floor markers) — the figure was regenerated in `5ab5210`, so it is presumably addressed, but confirming it needs a render.
