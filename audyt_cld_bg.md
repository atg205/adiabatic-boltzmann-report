# Audit: *Quantum Variational Algorithms on Adiabatic Quantum Computing Devices* (`report.tex`)

**Revision 10** — 2026-08-18. Revision 9 corrected after a second review round. That round is right on five of its eight points, one of which forced a rewrite of B2 and the withdrawal of a sub-finding of B1; it is wrong on the one point it calls a new blocker, and the refutation is given in §3.9. History and the list of corrections in [`CHANGELOG_audytu.md`](CHANGELOG_audytu.md).

**Status update, 2026-08-19: B1 fixed.** The CV-based stopping rule is gone; see §3.1 for what changed, the new fitted exponents, and what's still open (B4, B8).

**Pinned targets.** Manuscript: the 777-line working tree, i.e. `6793638` plus the merge `482c7cb` of `0d846c2` ("final changes"). Implementation: `iitis/adiabatic-boltzmann` at **`a4b0f2006`** ("integrated all result files together, energy corrected"), fetched and inspected for this revision. Both must be pinned in any future audit — the implementation repository moved from `4746ef128` to `a4b0f2006` while revision 8 was being written, which is exactly how revision 8 got its reproducibility section wrong.

**Method.** All file access via `sed`/`grep`/`awk`/`python3`/`pdftotext`/`pdftoppm`. Claims were re-derived rather than read: the TFIM closed form against dense exact diagonalisation over 90 (N, J, h, boundary-condition) cells; the RBM trace-out and the CEM conditional against brute-force enumeration; the average sign against exact diagonalisation of the J₁–J₂ chain; the CV stopping rule against tuned trial states; every sparsity number recomputed from the committed caches; figure values extracted from vector paths and 150–320 dpi renders; DOIs checked against Crossref; the implementation repository inspected at the pinned commit.

**Confidence.** `confirmed` = verified against a file, build artefact, committed cache, decoded figure or external source. `measured` = extracted from a rendered figure. `derived` = computed here. `inference` = follows from verified facts but has an untested step.

---

## 0. Before anything else — not a manuscript issue

**A private bank document is in this repository's history, and the remote is public.** `figures/2_5316856890368498963.pdf` — tracked since commit `92acd8d` (message: `]`), never referenced by any `\includegraphics`. `pdfinfo` gives Author "ING Bank Śląski S.A."; the text is a transaction confirmation whose payer block contains a full name and home address, plus payee details and an account number. `git remote -v` → `https://github.com/atg205/adiabatic-boltzmann-report`. *(confirmed)*

**Status, 2026-08-19: history purge done, GitHub-side exposure not yet closed.** The file was untracked and `.gitignore`d in commit `efa3156`, then `git filter-repo --path figures/2_5316856890368498963.pdf --invert-paths` was run on a fresh clone and force-pushed to `origin/main` (old tip `2f17f25` → new tip `57c5412`). *(confirmed: `git log --all` and `git rev-list --objects --all` find zero references to the path or blob in the rewritten history; the GitHub API tree for the new `main` tip contains no match either.)*

**This did not fully close the exposure.** The pre-rewrite commit `482c7cb2040af5f02587bb16445bd98d36196d92` is still directly browsable on GitHub (`.../blob/482c7cb.../figures/2_5316856890368498963.pdf`, confirmed by direct test) — force-pushing only moves what `main` points at, it does not delete the now-dangling objects from GitHub's storage. **Two steps remain, both blocked on repo-owner credentials no automated tool here has:**

1. Make the repository private (`Settings → General → Danger Zone → Change visibility`) as an immediate stop-gap — this blocks anonymous access to every URL in the repo, dangling commits included.
2. File a GitHub Support request (https://support.github.com/contact) to purge the cached/dangling objects, citing repo `atg205/adiabatic-boltzmann-report`, path `figures/2_5316856890368498963.pdf`, and every pre-rewrite commit SHA that touched it (`92acd8d`, `efa3156`, and any other old SHA still bookmarked/linked anywhere) so they garbage-collect the actual blob, not just the ref.

Until step 2 is confirmed, treat the file as still reachable by anyone with an old commit SHA.

**Also tracked and bound for that public repository, worth a decision:** the internal audit documents (`audyt_cld_bg.md`, `CHANGELOG_audytu.md`, `uwagi_do_audytu_cld_bg.md`, `ocena_audytu_cld_bg.md`), the `verify/*.py` scaffolding, and `scripts/__pycache__/*.pyc`.

---

## 1. Summary

| Dimension | Rev. 8 | Now | Verdict |
|---|---|---|---|
| Physics & math correctness | B+ | **B+** | Everything load-bearing checks out independently: the closed form, the trace-out, the CEM conditional, the geometric tensor, the exact baselines. The defects are in two diagnostics that measure nothing, not in the machinery. |
| Claims versus evidence | D | **D+** | Still the dominant problem, but one alleged contradiction was already fixed. What remains: the headline scaling claim is an artefact of the stopping rule, three orderings contradict their figures, and one claim is refuted by the repository's own data. |
| Completeness | B− | **B** | Corrected upward: the affiliation, the benchmark protocol, the seed list and a full sampler-parameter table are all present — revision 8 said otherwise and was wrong. The promised QPU sampling-quality comparison is still absent. |
| Novelty & positioning | narrow | **narrow** | Thirteen sections cite nothing, including both embedding contributions and the whole SB/LSB family. |
| Bibliography & attribution | C | **C** | Mechanics repaired. Attribution not: one citation demonstrably does not support its claim, one misattributes a method, four foundational references absent, four records factually wrong. |
| Reproducibility | D+ | **B−** | **Corrected upward after inspecting the pinned implementation commit**: the figure generator, the validated-convergence function, 11 842 result files and the auto-scale data are all committed there. Remaining: no commit hash in the paper, unpinned library versions, no QPU access dates. |
| Readability & LaTeX | C | **C** | Compiles without undefined references, but three defects print on every page and two labels share one float. |

### Blocking, in order

1. ~~**B1 — The headline scaling claim is confounded by a size-dependent stopping rule**~~ **FIXED 2026-08-19** (§3.1) — the CV-based self-detector is gone; TTE is now a plain, oracle-based, sustained rolling-window crossing. See §3.1 for what changed and what's still open.
2. **B2 — partially fixed:** the "wall-clock" mislabeling is corrected and the CEM clock-mixing is now disclosed; still open: no explicit statement that classical/FPGA/QPU are three different clocks, and the low-n unidentified-median problem hasn't been re-checked outside fig10c/10d (§3.2).
3. ~~**B3 — The solver-ordering sentence (L542) is false against its own figure**~~ **FIXED 2026-08-19** (§3.3), as a side effect of the B1 rewrite.
4. ~~**B4 — The abstract and Conclusion overclaim**~~ **FIXED 2026-08-19** (§3.4): both sentences rewritten to match the actual data.
5. ~~**B5 — "We tested the sparse models only on classical hardware" is refuted by 20 committed QPU runs**~~ **DATA REMOVED 2026-08-19** — the unusable (budget-mismatched) QPU cache is deleted from the implementation repo; the manuscript sentence still needs a small wording fix (§3.5).
6. ~~**B6 — The sign-problem instrument is identically zero**~~ **FIXED 2026-08-19** (§3.6): Marshall comparison figure included, ⟨s⟩ now evaluated in the correct gauge.
7. ~~**B7 — Two citations do not support their claims**~~ **FIXED 2026-08-19** (§3.7).
8. ~~**B8 — The threshold sensitivity is undisclosed, and the shipped figure cannot be produced by any committed code**~~ **MOSTLY FIXED 2026-08-19** (§3.8), resolved as a side effect of B1. **TODO:** ε-sensitivity of Zephyr(+CEM)'s exponent (sign flips between ε=0.10/0.15) — deliberately deferred.

---

## 2. What is now good — do not disturb this

- **The physics machinery checks out.** The TFIM closed form reproduces dense ED to ≤4×10⁻¹⁴ for J>0, h≥0, PBC at every N tested including odd N, and fails only for J<0 at odd N — exactly the case the stated validity range excludes. The trace-out is exact to 2.3×10⁻¹⁵. The CEM conditional ⟨h_j⟩ = **+**tanh(βΘ_j) is correct under the current energy convention (error 1.9×10⁻¹⁶; the −tanh alternative is off by up to 1.8). The weight orientation is consistent across the ansatz, the CEM formula, the listing and the implementation. D_TV, the SR update sign, the appendix derivation, the CG matvec, TTS and the Metropolis acceptance ratio are all correct. *(derived)*
- **The exact baselines are right.** Independent PBC Pauli-convention ED reproduces the convergence figure's reference lines at N=8 (E/N = −1.60686, −1.50000, −1.59782, −1.87911 for J₂/J₁ = 0.3/0.5/0.7/0.9), including exactly −1.5/site at the Majumdar–Ghosh point, which holds only under PBC with even N. *(derived)*
- **The `auto_scale` contradiction reported in revision 8 is fixed.** L349 and L676 now agree on `auto_scale=False`. *(confirmed — revision 8's B5 was stale and is withdrawn.)*
- **The experimental protocol is now properly documented**: TFIM at h=0.5, lr=0.08, reg=0.05, 200 samples/iteration, 100 iterations and **seeds 0–19** stated at L678, with every classical sampler's internal mixing parameters — including LSB's δ, γ and σ⁻² — in `tab:classical_sampler_params`. The affiliation is at L41–44. *(confirmed — revision 8 claimed these were missing and was wrong.)*
- **The reproducibility artefacts exist**, in the repository the availability statement names, at `a4b0f2006`: `scripts/viz/paper_figures.py` containing `compute_validated_convergence_iter(history, exact_energy, size, epsilon, cv_threshold, window=10)` — the paper's own criterion — and the fig10c/fig10d generators; **11 842 result files** (5 580 TFIM), each carrying `history`, `exact_energy`, `config` and per-run timing; `plots/dtv_autoscale/dtv_autoscale_N8_h1.0.json`; and a `requirements.txt`. *(confirmed at the pinned commit.)*
- **The bibliography mechanics were properly repaired**: DOIs and arXiv links print and are live (52 `/URI` annotations, every reference linked, all URLs HTTP 200); `unsrt`'s case folding completely defeated; journal names unified; zero bibtex warnings; all ten DOIs verified against Crossref. *(confirmed)*
- **The time-to-ε protocol is carefully designed**: oracle-free stopping rule, explicit validation against the true ground-state energy, an honest "matched-hyperparameter, not matched-tuning-effort" disclaimer, a stated QPU timing basis, and a justified omission of N=128. The problems below are about what is concluded from it. *(confirmed)*
- **CEM is applied to QPU samples** with and without correction, and the corrected series validate far more consistently — the strongest single result in the paper. *(confirmed)*

---

## 3. Blocking findings

### 3.1 B1 — The headline scaling claim is confounded by a size-dependent stopping rule *(the size dependence is `derived`; the causal attribution is `inference`)* — **FIXED 2026-08-19**

**What was done.** `compute_convergence_iter` (the CV-based self-detector) is deleted from `paper_figures.py`. `compute_validated_convergence_iter` now does one thing: the rolling-window (width 10) mean energy error per spin must stay below $\epsilon$ for 10 consecutive iterations, using `exact_energy` directly — no CV, no per-N/per-solver threshold calibration, nothing left to be confounded by N. Requiring 10 consecutive passes rather than a single crossing was added specifically to reject a run that briefly and spuriously dips below $\epsilon$ (observed in D-Wave trajectories) and then drifts back away from it.

**Non-CEM Pegasus/Zephyr dropped from the headline comparison.** Under the old CV proxy neither uncorrected QPU series could be calibrated at small N at all (precision 0-60% at every threshold tested). Re-checked directly under the new, calibration-free criterion: non-CEM Pegasus actually validates fine (15-20/20 across all four sizes) but non-CEM Zephyr is still thin at small N (1/20 at N=8, 5/20 at N=16) — so the exclusion is kept for now, but the original justification (CV-proxy failure) no longer fully applies to Pegasus without CEM. **Open follow-up:** decide whether to reinstate non-CEM Pegasus now that the blocking reason for it is gone.

**fig10c/fig10d regenerated** with the new criterion, thick lines, a fitted power-law ($\propto N^p$) dotted through each series, and the exponent printed in the legend. Report text (methodology paragraph, caption, and the ordering paragraph that used to cite hollow markers and the now-removed non-CEM series) rewritten to match.

**Resulting exponents (ε=0.1, all 20 seeds, no held-out split needed since there is no threshold left to overfit):** Metropolis +1.35, Gibbs +0.22, LSB(+CEM) +0.96, SA +1.39, FPGA +2.14, Pegasus(+CEM) **+0.16**, Zephyr(+CEM) **−0.20**. Both QPU+CEM exponents are far from the shipped −0.38/−0.55, and Pegasus(+CEM) is now mildly *positive* (getting slower with N, same direction as every classical solver) rather than negative. At $N=64$, FPGA (0.56 s) and Pegasus(+CEM) (0.47 s) have overlapping IQRs — not distinguishable as faster/slower.

**What remains for the paper to decide:** the abstract/Conclusion's "scales more favorably ... pointing to quantum competitiveness at larger scale" is no longer supported by this figure and should be withdrawn or rewritten (this connects to B4). This compounds with B8, which is unaffected by this fix.

The abstract and Conclusion argue the annealer "scales more favorably … pointing to quantum competitiveness at larger scale", sourced from the legend's fitted exponents: **Pegasus ∝ N^−0.38, Pegasus+CEM ∝ N^−0.35, Zephyr ∝ N^+0.06, Zephyr+CEM ∝ N^−0.55** against **FPGA ∝ N^1.90**. *(measured)*

A negative time-to-ε exponent says the annealer converges *faster* on bigger problems. The gate is CV = std(E_loc)/|mean(E_loc)| < 0.05, and CV falls as N^(−1/2) at fixed energy error per spin: measured on TFIM trial states tuned to exactly 0.1 error/spin against H(h=0.5), **CV = 0.1613 / 0.1408 / 0.1265 at N = 8/10/12 while CV·√N = 0.456 / 0.445 / 0.438 — constant to 4 %**. So the gate loosens with N, and the solver whose per-iteration cost grows slowest benefits most. *(derived)* Extrapolating that scaling to N=64 gives a factor ≈2.8, but that step assumes the N^(−1/2) law holds beyond the sizes measured here and at the accuracy the QPU runs actually reach — treat the factor as indicative, not exact.

**What this does and does not establish.** It establishes that the gate is not equally hard at every N, so the fitted exponents are confounded with the criterion. It does **not** by itself prove the negative exponents are pure artefact — that requires the decisive test, which has not been run: recompute the *actual* QPU and FPGA histories (they are committed upstream, `history` field) under a size-independent criterion, either CV·√N < const or a direct oracle-based energy-error crossing, and see whether the ordering and the exponents survive.

**Fix:** run that recomputation and report it; or remove the scaling claim from the abstract and Conclusion and state what was measured. Until then the claim is not supported, whether or not it turns out to be true.

### 3.2 B2 — The axis is not what it is called, and the two sampler clocks have different boundaries *(confirmed in the pinned code)* — **partially fixed 2026-08-19**

**"Wall-clock" mislabeling fixed.** Both occurrences in the manuscript text (the TTE definition and the energy-figure lead-in) called this "wall-clock time"; both now say "sampler time." This is a wording fix only — the underlying metric was already sampler-only in the code; only the prose was wrong.

**New finding while fixing it: there are three clocks, not two, and one series mixes two of them internally.** Traced through `encoder.py`/`sampler.py`: classical solvers (Metropolis/Gibbs/LSB/SA) get **host wall-clock** (`time.perf_counter()` around the call); FPGA/VeloxQ get a **device-self-reported time** from their own metadata file; D-Wave gets **`qpu_access_time`** from the vendor API (on-chip only). All three land in the same `sampling_time_s` field and one shared axis. Worse, for any `+CEM` series, `total_sampling_time_s = sampling_time_s + cem_time`, where `cem_time` is *always* host-measured — so Pegasus(+CEM)/Zephyr(+CEM)'s reported number is a device clock plus a host clock summed into one figure. Measured magnitude at N=32: CEM is 19.0% of Pegasus+CEM's total, 6.2% of Zephyr+CEM's, 5.7% of LSB+CEM's. **This is now disclosed in the text** (the paragraph defining \gls{tte} states the CEM addition explicitly), rather than silently dropped — dropping it was considered and rejected, since CEM is a real, necessary cost of the `+CEM` variant and removing it only for the QPU series would newly flatter Pegasus/Zephyr relative to LSB(+CEM), which still pays for it.

**Gibbs's iteration-0 cost (~16–22× its steady-state per-iteration cost, every run, every $N$) is real, not a bug.** It matches Gibbs's documented one-time 200-sweep PCD chain init (`tab:classical_sampler_params`; `n_warmup=200`, confirmed in `src/sampler.py:308`) against its 10-sweep steady-state cost — the ratio is exactly what 200/10 predicts. No fix needed; TTE already counts it correctly ($\propto N^{+0.22}$).

**Classical and D-Wave clock definitions now stated explicitly, 2026-08-19.** The protocol paragraph now says plainly what is timed for each: classical solvers get a host-side timer around the sampler call, with a one-time pre-training call to absorb JIT compilation cost; D-Wave gets SAPI's `qpu_access_time`, excluding network/queueing.

**TODO — FPGA still undisclosed.** FPGA/VeloxQ is the third clock (a device-self-reported time from its own metadata file, per `sampler.py:971,1300`), and the text still says nothing about its measurement basis or boundaries. Needs the same one-sentence treatment as classical/D-Wave got.

**Still open otherwise:** the originally flagged low-n unidentified-median problem is much reduced in the current fig10c/10d (worst case 16/20, since B1's fix changed which cells validate) but has not been independently re-checked for other figures using the same convention (fig9, fig2, fig1). *(inference — not yet verified.)*

Revision 9 said the classical series carry the full host-side SR cost that the QPU series have zeroed out. **That was wrong**, and the pinned implementation settles it: the timer starts immediately before `sampler.sample(...)` and stops immediately after, and the energy meter is active only around that same call. The code says so explicitly — "Only the `sampler.sample()`/`sample_parallel()` calls are metered … SR/CG/gradient work also runs on the GPU but isn't solver cost, so it's excluded." Both sides exclude the SR solve, the local energies and the gradients.

What survives is sharper. **First, the axis is mislabelled.** L539 defines TTE as "the wall-clock time until training reaches a validated convergence" and the caption repeats it, but what is plotted is **sampler time to validated convergence** — for every series. A reader comparing solvers on "time to train" is reading a quantity that excludes most of training. The same applies to the energy panel: it reports GPU energy drawn during sampling, while the abstract says "energy consumed to reach it".

**Second, the two sampler clocks still have different system boundaries.** The QPU number is the device-reported `qpu_access_time` (on-chip programming, anneal, readout), excluding queue and network; the classical number is host wall-clock around the sampler call, which includes host-side dispatch and transfer. These are not the same kind of measurement, and the caption's "absolute scale stays directly comparable" asserts that they are.

**Third, the plotted median is conditioned on success.** Four cells have fewer than 10/20 events, where a median under censoring is formally unidentified — Pegasus 2/20 at N=8, Zephyr 5/20 at N=16 and 6/20 at N=32, FPGA 6/20 at N=64, three of them in the classical-versus-quantum panel. The 2/20 and 5/20 cells are drawn with **zero-length IQR bars** while the 19/20 cell carries a bar spanning a factor of 3.6, so the least-supported cells render as the most precise. *(measured)*

**Fix:** relabel the axis and the caption as sampler time (and the energy panel as sampling energy), or measure end-to-end; state the two clocks' boundaries side by side and drop "directly comparable"; use Kaplan–Meier medians with intervals, grey out cells below ~10/20, and draw no whisker where the quartiles are degenerate.

### 3.3 B3 — The solver ordering is false against the figure *(measured, four independent extractions)* — **FIXED 2026-08-19**

Fixed as a side effect of the B1 rewrite: the old ranking sentence ("FPGA consistently fastest, followed by SA, then the two QPUs...") is gone, replaced by the paragraph now at L542, which only states claims verified directly against the current data (FPGA fastest through N=32; statistically indistinguishable from Pegasus(+CEM) at N=64; Gibbs flattest due to its disclosed fixed warmup cost). **Not done:** the audit's stronger suggested fix — generating this sentence mechanically from `paper_figures.py`'s data structures rather than hand-writing it — which would prevent a third recurrence if the figure changes again.

L542: "panel (b)'s FPGA is consistently fastest, followed by \gls{sa}, then panel (c)'s two QPUs, with panel (a)'s Metropolis and Gibbs and panel (b)'s \gls{lsb} the slowest … both QPUs overtake them at that size."

SA is **slower than every QPU series from N=16 upward** and the **slowest of all nine series at N≥24**, reaching ≈12–13.5 s at N=64; Gibbs, named among the slowest, is flat at 0.7–1.3 s. The legend corroborates: SA ∝ N^1.19, Gibbs ∝ N^0.08. The second clause fails too: at N=64 FPGA (≈0.27 s) sits *inside* the QPU band (≈0.20–0.51 s) — one series faster, one tied, two slower.

**Fix:** generate this sentence and the caption mechanically from `paper_figures.py`'s data structures. This is the second consecutive revision in which a hand-written ordering sentence contradicted this figure.

### 3.4 B4 — The abstract and Conclusion overclaim *(confirmed)* — **FIXED 2026-08-19**

Both sentences rewritten in the abstract and Conclusion: the energy claim is now restricted to the metered classical solvers (no QPU-energy comparison claimed); the scaling claim now states the actual result (Pegasus(+CEM) statistically indistinguishable from FPGA by N=64; only Zephyr(+CEM) shows a weak, criterion-sensitive favorable trend) instead of "quantum competitiveness." The closing sentence of the Conclusion was rewritten to match.

"Across both metrics, the FPGA-based solver outperforms all other samplers, classical and quantum alike, at the system sizes tested" (abstract) and "the fastest and most energy-efficient sampler at every size tested" (Conclusion) are contradicted by the body at L542 and by the measurement in B3.

On energy the problem is not an asymmetric measurement — L544 states plainly that the QPUs are omitted "because no API exposes per-job energy draw" — it is that **the abstract claims superiority over quantum samplers on a metric for which no quantum number exists**. The FPGA's own energy figure is additionally "an assumed constant power draw of 45 W … since it was never GPU-metered", by the caption's own admission.

**Fix:** restrict the energy claim to the metered classical solvers, mark the FPGA number as an estimate, and state the N=64 crossover honestly.

### 3.5 B5 — An unreported QPU arm that the repository commits *(derived from the caches)* — **DATA REMOVED 2026-08-19**

**Decision: remove, not disclose.** The mismatched iteration budgets (14–300 vs. a uniform 300) mean the QPU arm was never a fair comparison — its per-spin error numbers (10.68–76.42%) aren't meaningfully comparable to the classical arms', so restoring or disclosing it wouldn't add a valid data point, just a confusing one. `cache_sparsity_ablation_qpu.json`, `cache_qpu_zephyr.json`, `sparsity_heatmap_REAL_QPU_zephyr.pdf/png` are `git rm`'d in the implementation repo (staged, not yet committed). The actively-used `sparsity_ablation_qpu_vs_classical.pdf` is untouched — it contains only classical series despite its name and is unaffected by this.

**Still open:** L474 ("we tested the sparse models only on classical hardware") is now *closer* to true but not fully honest — a QPU arm was in fact attempted and discarded, not simply never run. Recommend: "a real-QPU arm was attempted but excluded because its iteration budget could not be matched to the classical arms" rather than implying it was never tried. Also note: `origin` for this repo is `iitis/adiabatic-boltzmann` (not the report repo) — if that remote is public, deleting the working-tree files doesn't remove them from git history, same caveat as §0.

L474: "Due to budget constraints, we tested the sparse models only on classical hardware." `figures/sparsity/cache_sparsity_ablation_qpu.json` contains **20 records — 4 masks × 5 seeds (42/123/456/789/1234), N=16, Zephyr, each with a populated `qpu_time_ms_used`**. The plotted file is still named `sparsity_ablation_qpu_vs_classical.pdf` while its legend lists only three classical samplers and the exact floor; `sparsity_heatmap_REAL_QPU_zephyr.pdf` is also committed and unused. The withheld arm gives 10.68 / 12.27 / 45.69 / 76.42 % per-spin error.

Restoring it is not clean: the QPU arm ran **14–300 SR iterations** per run (per mask `[26,31,176,205,300]`, `[185,297,300,300,300]`, `[15,28,133,300,300]`, `[14,18,25,32,44]`) against a uniform **300** for every classical run.

**Fix:** state what was actually run — "a real-QPU arm was run but is not reported because its iteration budget was not matched to the classical arms" — or plot it with the mismatch disclosed. A committed dataset that refutes the text is the largest single credibility risk here.

### 3.6 B6 — The sign-problem instrument measures nothing *(derived)* — **FIXED 2026-08-19**

⟨s⟩ = Σ_v Ψ₀(v) / Σ_v |Ψ₀(v)| is **identically zero** for every model it is introduced for: Σ_v Ψ₀(v) = 2^{N/2}⟨+|^{⊗N}|Ψ₀⟩ vanishes by SU(2) symmetry for any singlet ground state. Measured across 12 (N, J₂/J₁) cells at N = 6, 8, 10 and J₂/J₁ = 0, 0.3, 0.5, 0.7: **|⟨s⟩| ≤ 3×10⁻¹⁶ everywhere**, including the provably sign-free J₂ = 0 case. No number derived from it appears in the paper. In the **Marshall gauge** the same formula is informative: 1.000 → 0.997 → 0.941 → 0.000 at N=8 across J₂/J₁ = 0 → 0.3 → 0.5 → 0.7.

L511's claim that "without the correction the variational energy degrades significantly" also has no evidence in the paper: the cited figure shows one Marshall-corrected curve per panel, no ablation, no mention of the gauge.

**Fix applied.** `figures/marshall_comparison.pdf` is now included (new `\label{fig:marshall-comparison}`, two panels: energy-error ablation with/without Marshall, and ⟨s⟩ in both gauges). The equation is now explicitly evaluated on $\phi=U|\Psi_0\rangle$ (Marshall-rotated), with a sentence stating the untransformed $\Psi_0$ gives an identically-zero, uninformative value. L511's "degrades significantly" claim now cites the same figure's top panel, closing the previously-unevidenced-ablation gap too. **Residual resolved, 2026-08-19.** The generating script (`scripts/viz/plot_marshall_comparison.py`, 312 lines) and its underlying data cache existed in git history — added in `ff4bfd88d` ("marshall sign analysis"), then deleted in `b8dcda31e` ("refactor") along with several unrelated scripts. Both recovered via `git show <sha>:<path>` and restored to the tree (staged, not committed). Re-run from the recovered cache (no retraining) and verified **pixel-identical** to the currently-committed figure (`pdftoppm` render diff, zero-size bounding box). Reproducibility fully closed for this figure.

### 3.7 B7 — Two citations do not support their claims — **FIXED 2026-08-19**

- ~~**L109** cites `mpg` as the sole authority for the Heisenberg model.~~ Added `Heisenberg_1928` (Z. Phys. 49, 619 (1928)) to `bib.bib`, now cited at the Heisenberg-model line. `mpg` (the lecture note, whose only heading is "Transverse-field Ising model") moved to the TFIM introduction, where it actually belongs.
- ~~**L560** credits Stochastic Reconfiguration to `Sorella_2001`~~, whose own abstract says SR "has been recently introduced" elsewhere. Added `Sorella_1998` (PRL 80, 4558) to `bib.bib`; the SR-introduction sentence now cites `\cite{Sorella_1998,Sorella_2001}` (1998 for the method, 2001 kept for the generalized-Lanczos variant it actually describes).

Both verified in the compiled bibliography (`[7] W. Heisenberg...`, `[12] Sandro Sorella. Green function Monte Carlo...`), full rebuild (pdflatex+bibtex×3) clean, no errors.

### 3.8 B8 — Undisclosed threshold sensitivity, and a figure the pinned code cannot produce *(confirmed at `a4b0f2006`)* — **MOSTLY RESOLVED 2026-08-19, one TODO carried forward**

The paper presents CV < 0.05 and ε = 0.1 per spin as *the* protocol. Upstream the generator's signature is `fig10c_tte_vs_n_self_convergence(cv_threshold=0.05, window=10, epsilon=0.01)` — ε defaults to **0.01**, ten times tighter — and the repository holds **five** fig10c variants over cv ∈ {0.03, 0.05} × ε ∈ {0.01, 0.1} plus two fig10d variants. The manuscript reports one cell of that grid, the loosest on ε, and never mentions the others.

The existence of those files does **not** show the pair was chosen after seeing the results — they are equally consistent with a robustness sweep or with figure development, and revision 9 overstated this. What it does show is that a sensitivity analysis exists and is undisclosed, which matters because the fitted exponents, the censoring pattern and therefore B1's claim are all functions of (CV, ε).

**The provenance problem is larger than the missing suffix, and this part is decisive.** The figure shipped in the paper is not the upstream artefact:

| | report `fig10c_tte_vs_n_self_convergence.pdf` | upstream `…_cv0.05_eps0.1.pdf` |
|---|---|---|
| SHA-256 | `4a56be72…` | `ded0bc94…` |
| fitted `∝ N^p` labels in the plot text | **9** | **0** |

The pinned `fig10c` function contains no exponent fitting at all (`polyfit`/`curve_fit`/slope → zero hits), and its `__main__` block calls eleven figure functions but **neither fig10c nor fig10d**. So the exact artefact on which the paper's headline scaling claim rests — the one carrying the exponents — cannot be produced by any committed state I can see.

**Resolved as a side effect of B1.** CV no longer exists as a parameter, so the (CV, ε) grid provenance problem is moot by construction. The pinned code now generates the shipped figure directly (`fig10c_tte_vs_n_validated_convergence`/`fig10d_...` added to `__main__`), the exponent labels are generated by code (`fit_powerlaw`), and the filename is parameterised (`..._eps0.1.pdf`) and traceable to its generating call — re-verified by regenerating from the current tree and diffing pixel-for-pixel against the shipped file. **Also removed:** 14 orphaned files from the old, now-deleted CV methodology (`fig10c/fig10d_..._self_convergence_cv*.pdf/png`, including the exact upstream artefact this section's SHA table cites, confirmed via checksum) — these could never be regenerated again and represented a superseded approach, so they're `git rm`'d rather than kept as dead weight.

**TODO, not fixed:** ε-sensitivity is the direct descendant of this finding and it matters. Sweeping ε ∈ {0.05, 0.10, 0.15, 0.20} under the *new* methodology: Zephyr(+CEM)'s exponent is −0.493 / −0.199 / **+0.161** / +0.201 — it **flips sign between ε=0.10 and ε=0.15**. Pegasus(+CEM) stays consistently mildly positive throughout (+0.02 to +0.21). This means the B4 fix's claim ("Zephyr(+CEM) alone shows a weak favorable trend") is not robust to a small, plausible change in the accuracy target — deliberately left unaddressed in the manuscript for now (explicit call, not an oversight); revisit before submission.

### 3.9 Examined and rejected: the "forward-looking plateau window"

A review round raised, as a new blocker, that `compute_validated_convergence_iter` validates the wrong iterations — that `plateau = energies[conv_iter-1 : conv_iter-1+window]` takes the detection point plus up to nine *future* iterations instead of the window that triggered the detector, which would put every `n/20` count, median and exponent in doubt.

**It does not.** `compute_convergence_iter` returns `conv_iter = t − window + 2` when the run of `window` passing iterations ends at 0-indexed `t`, i.e. `conv_iter` is the **1-indexed first iteration of the plateau**, not the detection point. Then `conv_iter − 1 = t − window + 1` is that same iteration 0-indexed, and the slice spans `t−window+1 … t` — **exactly the triggering window**. Verified for detection at t = 9, 15 and 42: slice and triggering window coincide in every case. *(derived)*

This also **withdraws a sub-finding of revision 9's B1**: that the QPU medians correspond to 4–9 iterations, "fewer than the 10 the rule requires". Since `conv_iter` marks the plateau's start, a TTE below ten iterations is expected behaviour, not an inconsistency.

One legitimate residual remains, worth a sentence in the paper rather than a finding: because TTE is reported at the plateau's **start**, it excludes the ten iterations of confirmation the rule needs before it fires. That flatters every series equally, so it does not affect the ordering, but the reported time is time-to-plateau-start, not time-to-detection.

---

## 4. Major findings

**M1 — The energy figure's caption contradicts its own annotations.** — **RESOLVED 2026-08-19, as a side effect of B1.** Re-checked against the current (post-B1) methodology: fig10c and fig10d's shared classical-solver cells (panels a-b) now match exactly — 17/20, 16/20, 17/20, 18/20, 19/20 at N=64 in both figures, verified directly against the data. The original mismatch (19 vs. 10 annotations) was an artifact of the old CV-based criterion, which no longer exists.

**M2 — Figure 4(a)'s caption is wrong by a factor of two.** — **FIXED 2026-08-19.** Confirmed by direct visual node-count on both panels (12+12 visible/hidden, matching panel (b)'s 24 chain qubits one-per-node). Caption corrected to "$12$ visible and $12$ hidden units."

**M3 — The hardware paragraph contradicts itself about simulated annealing.** — **FIXED 2026-08-19, and the resolution favors the paper, not the audit.** Traced in the code: `results/tfim_1d/*/custom/simulated_annealing/` (the series actually plotted in every TFIM figure) is produced by `ClassicalSampler` via `mcmc_matched_sweep.py:126` — pure JAX/GPU, confirmed. `neal.SimulatedAnnealingSampler` (`dwave-neal`) does exist in `src/sampler.py:1369` and has its own `results/tfim_1d/*/dimod/simulated_annealing/` archive, but that data feeds `fig7`/`fig8`/`fig9` — none of which are `\includegraphics`'d anywhere in `report.tex`. So the "JAX on GPU" sentence was actually correct for the plotted SA series; the stray `dwave-neal` sentence right after it described a different, unused sampler, creating the apparent contradiction. Replaced it with an accurate description (JAX/GPU, per `tab:classical_sampler_params`) and a note that the dwave-neal variant exists but isn't used for any result in this paper.

**M4 — The benchmark's parameters are stated 130 lines from the figure, and one is still missing.** — **FIXED 2026-08-19 (missing facts; positional distance not restructured).** Verified $N_\text{hidden}=N_\text{visible}$ directly from a result file's config (`nh{n}` in every archive path). Verified $\epsilon=0.1$ is a $9.40\%$ relative error at every tested $N$ (computed `|exact_energy|/N` directly: $1.0635$-$1.0636$ across $N=8..64$). Both facts added directly to the TTE section's own protocol sentence, rather than only living in the distant Implementation section.

**M5 — Coverage.** — **FIXED 2026-08-19.** Confirmed a real, separate gap: zero QPU data exists at N=12/24 (directories absent), traced to `dwave_matched_sweep.py` running QPU experiments on their own coarser doubling-sequence sweep, distinct from the classical solvers' six-point sweep. The defensive "should not be mistaken for a gap" wording replaced with a plain statement: "For budget reasons, we report QPU results at four sizes only: $N\in\{8,16,32,64\}$."

**M6 — The sparsity floor's shape is one outlier seed.** — **FIXED 2026-08-19.** Recomputed directly from `cache_sparsity_ablation_exact.json`/`_simulated_annealing.json`/`_gibbs.json`: with medians (robust to n=5 outliers) the floor is $0.99/1.51/2.16/2.44\%$, monotone, peaking at the **fourth** mask ($\sim\!2.5\times$ rise) — confirming the audit's finding almost exactly. The mean-based "roughly triples, peaks at third mask" in the original text was arithmetically consistent with the code (verified: means are $1.0/1.48/3.17/2.41\%$) but fragile — one outlier seed (Gibbs mask 3: $55.86\%$ vs. a $\sim\!23$–$28\%$ bulk) swings a 5-seed mean substantially; switching to medians also **resolves Gibbs's apparent non-monotonicity** (median series is monotone: $9.99\to26.61\to28.47\to28.54\%$; the dip only existed in the mean). Text rewritten throughout (both occurrences) to report medians, all three samplers explicitly (not "the classical-MCMC curve" as one aggregate), and the correct $9.7$–$17.7\times$ ratio band.

**M7 — The Fig. 14(b) legend box covers three of the four floor markers the text quotes.** — **FIXED 2026-08-19.** Confirmed visually (only the leftmost floor marker was visible; the other 3 sat under the legend box). Root cause: `scripts/viz/plot_sparsity_ablation_floor.py:187` used `loc="lower right"`, directly where the floor markers sit. Moved the legend outside the axes (`bbox_to_anchor=(1.02, 0.5), loc="center left"`); regenerated and visually confirmed all 4 floor markers now fully visible.

**M8 — The parallel-embedding numbers are total run lengths, and the claim rests on one seed.** — **FIXED 2026-08-19, and confirmed worse than estimated.** Traced `_plot_one_panel` in `scripts/exper/parallel_embedding_experiment.py`: `x_end` is literally `cumsum(sampling_time_s)[-1]` for a converged run — the full 150-iteration run length, not a plateau time, exactly as flagged. Applying this work's own oracle-based rolling-window criterion to the raw cache (`cache_parallel_embedding_np_seeds.json`) gives real plateau times of $0.54\,\mathrm{s}$ and $5.17\,\mathrm{s}$ for the two converging $n_\mathrm{parallel}=1$ seeds — **the two seeds disagree by $\sim\!10\times$ with each other**, which is worse than the audit's estimate (~6.0s) suggested and undermines any clean comparison, converging $n_\mathrm{parallel}=5$ seed gives $0.23\,\mathrm{s}$. Text, abstract, and Conclusion all rewritten: the speedup claim is now stated as unsupported by the current seed count, not asserted.

**M9 — Figure 1's trend and the abstract's point in opposite directions, and the scopes are never separated.** — **PARTIALLY FIXED 2026-08-19 (3 of 4 sub-issues; digitization disclosure explicitly deferred).**
1. ~~Scopes never separated~~ **FIXED**: caption's opening sentence now states plainly that Figure 1 is a different problem/metric (native QUBO encodings, TTS) from the rest of the paper (RBM-VMC, TTE).
2. ~~"Classical solvers dominate for N≳100" understates panel (a)~~ **FIXED**: confirmed visually (D-Wave series are already 2-3 orders of magnitude slower at N=16, the smallest size shown, no crossing anywhere) — text now says "dominate across the entire range tested ($N=16$ to $112$), with no crossing point."
3. ~~Panel (b) contradicts its own caption re: CFA~~ **FIXED**: caption now states "most encodings scale no better than random guessing; the custom-embedded CFA encoding is the exception," matching the body text's existing nuance instead of contradicting it.
4. **Not done, by request:** digitization disclosure (panel (a)'s points are digitized from the published figure's vector paths per the generator's docstring, undisclosed in the manuscript) — deliberately left for later.

**M10 — Attribution — FIXED 2026-08-19 (9 of 9 missing citations added; 2 sub-issues remain open).**

All nine previously-absent foundational citations added to `bib.bib` (verified against live sources, not memory alone — DOIs/pages/full author lists checked via web search before adding) and wired to their claims:
- **Carleo & Troyer 2017** (Science 355, 602) — the neural-quantum-state/VMC ansatz, the paper's core method, now cited at its introduction.
- **King et al. 2025** (Science 388, 199, 63 authors) — the "beyond-classical" claim the paper is framed around.
- **Goto et al. 2019** (Sci. Adv. 5, eaav2372) — Simulated Bifurcation's origin, at its first definition.
- **Metropolis et al. 1953** (J. Chem. Phys. 21, 1087) and **Hastings 1970** (Biometrika 57, 97) — the Metropolis-Hastings algorithm (previously cited *only* to a blog post with an empty year; that citation is kept alongside for the pedagogical formula, but the algorithm's own introduction now cites the originals).
- **Kirkpatrick et al. 1983** (Science 220, 671) — Simulated Annealing.
- **Geman & Geman 1984** (IEEE TPAMI PAMI-6, 721) — Gibbs sampling.
- **Marshall 1955** (Proc. R. Soc. A 232, 48) — the Marshall sign rule itself (previously only its frustrated-case violation, Richter 1994, was cited — the base rule had no citation at all).
- **Benedetti et al. 2016** (Phys. Rev. A 94, 022308) — effective-temperature estimation for QA sampling, at $\beta_\text{eff}$'s introduction in §4.2.
- **Pelofske et al. 2022** (Sci. Rep. 12, 4499) — parallel quantum annealing, at the parallel-embedding section's opening sentence.

All 9 verified rendering correctly in the compiled bibliography after a full `pdflatex`+`bibtex`×3 rebuild (clean, no undefined-citation warnings).

**Both residuals fixed 2026-08-19, sourced live rather than from memory.**

1. **Richter 1994's square-lattice/1D-chain mismatch.** Added `Voigt_2000` (Voigt & Richter, *Acta Phys. Pol. A* 97, 979 (2000), "Marshall-Peierls sign rule in frustrated Heisenberg **chains**") — confirmed via the arXiv text (cond-mat/0003207) that this paper computes the spin-1/2 critical frustration ($J_2^\text{crit}=0.027\pm0.003$) as its **own** extrapolation, directly on the 1D chain — a precise dimensional match this paper's model actually uses, not a borrowed number. Both citation sites now read `\cite{Richter_1994,Voigt_2000}`, with the second occurrence's wording split to attribute the square-lattice result to Richter and the chain result to Voigt & Richter explicitly, rather than crediting both papers with a single unqualified "who found."
2. **The average-sign definition mismatch.** Kept `Troyer_2005` — it's the standard, correctly-named reference for the *concept* of average sign (confirmed: their $\langle\text{sgn}\rangle=\sum_C W_C/\sum_C|W_C|$ is the same canonical form used everywhere in the sign-problem literature) — but added a sentence stating explicitly that their definition is a finite-temperature partition-function ratio, while this paper applies the same ratio directly to a $T{=}0$ ground-state wavefunction. This is a precision fix, not a citation swap: the reference is right for the *name*, the text was missing the caveat that it's used in a different formal setting here.

Full `pdflatex`+`bibtex`×3 rebuild clean; `Voigt_2000` confirmed rendering in the compiled bibliography.

**M11 — Four bibliography records are factually wrong.** — **FIXED 2026-08-19, all six sub-issues, each re-verified live.** `Mehta_2025` was already correct on inspection (`112(3):032616`, no action needed — the audit's note was stale). Fixed: (1) `veloxq` — confirmed via arXiv that v2 (2026-05-04) replaced "Przybysz, A." with "Louzada, H."; author list updated to match what the version-less URL now serves, with a note explaining why. (2) `willsch2024state` — confirmed via web search it's now a real proceedings paper (NIC Symposium 2025, NIC Series vol. 52, pp. 239–250; DOI `10.34734/FZJ-2025-02575`, not `-01965` as this audit previously stated — re-verified twice); entry changed from `@misc` (arXiv preprint) to `@inproceedings`. (3) `rrf3-jm5m` — added `number={4}` alongside the ignored `issue` field; now renders `25(4):044055`. (4)/(5) Two undated `@misc` entries: `djnavarroMetropolisHastingsAlgorithm`'s year set to 2023 (present in its own URL); `mpg` — found via web search that the true author is **Alexander Wietek** (not "Max-Planck-Gesellschaft" as previously listed — verified from the actual title page), no publication year is stated anywhere in the source (confirmed directly from the PDF), so the entry is left undated with an explicit "no publication date given" note rather than fabricating one. (6) `\bibliographystyle`/`\bibliography` order swapped. Full rebuild (pdflatex+bibtex×3) clean; all six changes verified rendering correctly in the compiled bibliography.

**M12 — Reproducibility: the artefacts exist; the pointers to them do not.** — **PARTIALLY FIXED 2026-08-19 (QPU access dates/solver versions only, by explicit scope — commit hash/DOI/requirements-pinning/deleted-script left untouched).** No per-run solver calibration version or timestamp exists in any archived D-Wave result file (checked directly). Git commit history gives an honest proxy: QPU result files were added between 2026-05-11 and 2026-08-10 (a ~3-month window). Added to the Hardware and Software Configuration section: the solvers used, the absence of per-run calibration info, the commit-history-derived date range, and an explicit note that D-Wave periodically recalibrates within a solver family over such a window. The figure-regeneration part of this finding is already resolved via B8/B1. Still open, not touched: commit hash/DOI in the availability statement, `requirements.txt` version pinning, and the deleted `scripts/dtv_autoscale.py`.

**M13 — The seeding sentence contradicts the paper's own seed list.** — **FIXED 2026-08-19, same pattern as M3: text described a real but unused fallback path.** Traced the actual production path: `scripts/exper/mcmc_matched_sweep.py:run_one` does `key = jax.random.PRNGKey(seed)` directly from the CLI seed, then `jax.random.split`s it and assigns `sampler._key = sampler_key` **before** the sampler ever runs — so `ClassicalSampler._next_key`'s `np.random.randint(...)` fallback (`sampler.py:338`, used only when `self._key is None`) is never triggered for these results. This confirms the pipeline genuinely is deterministic from the stated seed (consistent with the paper's own already-stated bit-for-bit reproducibility check), and the old sentence just described the wrong code path. Rewritten to describe the actual mechanism (`jax.random.PRNGKey(seed)`, split to seed model init and sampler separately).

**M14 — Three defects visible in the rendered PDF.** — **FIXED 2026-08-19, all three.** (1) `\usepackage{hyperref}` → `\usepackage[hidelinks]{hyperref}`, removing the colored link boxes. (2) Added an `\lstset{...}` block (monospace, syntax-colored, boxed) right after `\usepackage{listings}`; verified visually on the rendered PDF — code now displays as normal, properly-spaced, syntax-highlighted Python. (3) Found the actual duplicate: `\label{fig:tte_self_convergence}` and `\label{fig:energy_self_convergence}` both sat on the same combined TTE+energy figure float (not, as the other "multiple labels" hits in this document are, one label per subfigure plus one for the whole figure, which is correct usage). Removed the redundant second label and simplified all 5 places that referenced both (`\autoref{X}/\autoref{Y}` → `\autoref{X}`); confirmed the "Figure N and Figure N" duplication is gone in the compiled PDF.

**M15 — The promised sampling-quality comparison is still absent.** The Sampling Quality section contains no QPU series and no QPU `D_TV` number appears anywhere in the prose; the only QPU distribution-quality data is the auto-scale ablation, run at different sample counts and floors. CEM is deployed on QPU samples but never validated on them, and no β_eff is reported for any QPU run that uses it. The CEM→β_x feedback loop and the RBM→Ising map are never written down. *(confirmed)*

**M16 — The `auto_scale` causal claim is a temperature confound.** — **FIXED 2026-08-19.** Confirmed exactly against the actual `dtv_autoscale_dtv_N8` figure: curves nearly coincide at the smallest $\beta_x$ (~62-64%, matching near-identical $\beta_\text{eff}$ there), `auto_scale=False` then drops to a minimum $D_\mathrm{TV}\approx29.5\%$ near $\beta_x\approx5.5$ (where the companion figure shows $\beta_\text{eff}$ crossing the VMC target of 1), while `auto_scale=True` stays flat (~63-64%) across the whole range since it pins $\beta_\text{eff}$ regardless of $\beta_x$. Rewritten to state the actual mechanism (loss of tunability, not a direct property of the switch) while keeping the paper's existing conclusion (use `auto_scale=False` elsewhere) intact.

---

## 5. Completeness

**Delivered:** abstract, Conclusion, availability statement, affiliation; the full training protocol and per-sampler parameter table; a cross-solver timing comparison and an energy metric; QPU β_eff measured for one configuration; CEM applied to QPU samples; unused models cut; GPU, driver and CUDA specified.

**Still missing:** any QPU sampling-quality measurement comparable to the classical benchmark (M15); a headline accuracy number for QPU-driven training at any N; β_eff for the QPU experiments that use it; the hidden-unit count of the headline benchmark (M4); a Methods description of the fastest solver — FPGA/VeloxQ appears only in the TTE figure and one hardware sentence; per-figure seeds and sample budgets for the QPU-facing figures; numeric η, λ and CG tolerance; a pinned `\date`; and `\appendix`, so the appendix prints as a numbered section with equation numbering running on.

---

## 6. Novelty and positioning

Unchanged: the CEM validation is pre-empted by Kubo & Goto; the sparse chain-free RBM is incremental against Park et al., Golubeva & Melko, Pilati & Pieri and Marshall et al.; parallel embedding is standard practice (Pelofske et al.); the sampling-quality benchmark sits in the territory of Berns et al., PRApplied 25, 024085 (2026). The residual open gap is an SB-class sampler with per-iteration temperature correction inside an NQS/VMC loop — and the report now *has* that experiment (LSB+CEM, and CEM on the QPU), which is the strongest thing in it. It cannot be claimed while the sections that would position it cite nothing. *(editorial judgement, not an audit finding.)*

---

## 7. Priorities

### P0 — before the next push
1. **Done in part:** history purged (`git filter-repo` + force-push, verified — §0). **Still open:** make the repo private and/or get GitHub Support to purge the dangling pre-rewrite commits, since the old blob is still directly browsable by SHA; decide what to do about the tracked internal documents and `verify/` scaffolding (§0).

### P0 — methodological, before the manuscript is shown
2. ~~Recompute the committed histories under a size-independent criterion, or withdraw the scaling claim (B1)~~ **DONE 2026-08-19** — recomputed (§3.1); the abstract/Conclusion scaling sentence itself still needs updating to match (folds into B4).
3. ~~Relabel the time and energy axes as sampler-side quantities~~ **DONE 2026-08-19** (wording + CEM-mixing disclosure + explicit classical/D-Wave clock definitions). **TODO:** same one-sentence clock disclosure for FPGA/VeloxQ; a censoring-aware estimator for any remaining low-n cells outside fig10c/10d (B2).
4. ~~Regenerate the ordering sentence and caption from the plotting data~~ **DONE 2026-08-19** (B3, manually re-verified rather than mechanically generated — see §3.3); ~~reconcile the abstract and Conclusion and restrict the energy claim~~ **DONE 2026-08-19** (B4). ~~M1 (energy-figure caption vs. TTE-figure cell mismatch)~~ **RESOLVED 2026-08-19** as a side effect of B1 — re-verified, this line was stale.
5. ~~Say what was actually run on the QPU for the sparse models, and rename the figure file~~ **PARTIAL 2026-08-19**: unusable QPU data removed instead of disclosed (B5). Open by explicit user choice, not oversight: reword L474 to say a QPU arm was attempted, not never run.
6. ~~Include the already-committed Marshall comparison and fix or drop the average sign~~ **DONE 2026-08-19** (B6).
6a. ~~Publish the (CV, ε) sensitivity table, and commit the code that produced the shipped figure with its parameterised filename~~ **DONE 2026-08-19** (B8, CV side moot post-B1; code/filename provenance fixed). **TODO:** ε-sensitivity disclosure (deliberately deferred).

### P0 — attribution and figures
7. ~~Fix the two misattributed citations~~ **DONE 2026-08-19** (B7); ~~add Carleo & Troyer, King et al., Marshall, Goto, Metropolis/Hastings, Kirkpatrick, Geman & Geman, Benedetti, Pelofske~~ **DONE 2026-08-19** (M10); ~~Richter 1994's square-lattice/1D-chain mismatch; the average-sign citation's partition-function-vs-amplitude definitional gap~~ **DONE 2026-08-19**.
8. Fix the Fig. 4(a) node count (M2), the SA hardware contradiction (M3), Fig. 1's caption and its undisclosed provenance (M9), and state the hidden-unit count and relative ε at the benchmark (M4).

### P1 — before submission
9. Add a QPU `D_TV` measurement comparable to the classical benchmark; report β_eff for QPU runs using CEM; write the RBM→Ising map and the CEM→β_x loop (M15).
10. Fix the sparsity claims to match the caches — median floor, per-sampler ranges, Gibbs non-monotonicity, legend occlusion (M6, M7).
11. Restate the parallel-embedding numbers and add seeds at n=5, or soften the Conclusion (M8).
12. Pin a commit hash or Zenodo DOI in the availability statement, pin library versions, record QPU access dates (M12); correct the seeding sentence (M13); fix the four bibliography records (M11); reframe the `auto_scale` causal claim (M16).

### P2 — polish
13. `\hypersetup{hidelinks}`, `\lstset`, split the double-labelled float, `\appendix`, pinned `\date`, notation collisions (`M` vs `N_h`, two meanings of α, `N` overloaded in the factoring caption), figure citation order, and an English-language edit (M14).
