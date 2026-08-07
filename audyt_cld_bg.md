# Audit: *Quantum Variational Algorithms on Adiabatic Quantum Computing Devices* (`report.tex`)

**Target:** `report.tex` as last changed in commit **`5bc5a64`** ("added dwave beta scaling section") — **772 source lines, 23 compiled pages, 32 numbered equations, 15 figures**. The repository HEAD moves independently of the manuscript (it is `634bb39` at the time of writing), so verify the target with `git log -1 --format='%h' -- report.tex` (→ `5bc5a64`) together with `wc -l report.tex` (→ 772) and `sed -n '772p'` (→ `\end{document}`). Equation and figure numbers are anchored to `build/report.aux`.

**Revision 5** (2026-08-07). Revision 4 verified the author's fixes to revision 3; revision 5 corrects revision 4's own errors following a reviewer critique — principally an over-generalisation of the auto-scale measurement and a false positive in the reproducibility section. History in [`CHANGELOG_audytu.md`](CHANGELOG_audytu.md).

**Where things stand.** Of revision 3's 26 findings: **20 verified fixed, 2 obsolete, 2 partially fixed, 1 not fixed, 1 fixed with a new contradiction** — no `(FIXED)` annotation was false. The ~136 lines added since then contain **5 blocking defects, 9 substantive ones, and 10 cosmetic ones**. The physics is no longer the problem; presentation and reproducibility of the new experiments are.

**Confidence labels:** `confirmed` (verified numerically, against a build artefact, a committed cache, or by decoding the figure), `strong inference`, `cannot verify here`. Reproduction scripts in [`verify/`](verify/): `cem_family.py`, `cem_objective.py`, `tfim_e0.py`, `cache_budget_stats.py`.

> **Numbering shifted since revision 3.** Equations: old (8)→(8) L145, (10)→L214, (13)→L242, (16)→L256, (20)→**(19)** L426, (28)→**(27)** L655. Figures: old "Fig. 9"→**Figure 5**, "Fig. 12"→**Figure 14**, "Fig. 13b"→**Figure 15b**. New: **Figure 7** (time-to-ε), **Figure 9** (auto-scale).

---

## 1. Summary

| Dimension | Rev. 3 | Now | Verdict |
|---|---|---|---|
| Physics & math correctness | B− | **B** | F1 fixed at the source; exact solver, ansatz, SR/CG and sign conventions all sound. What remains are new claims that contradict their own figures. |
| Completeness | C | **C+** | Three formerly-critical gaps closed: QPU β_eff measured, a QPU `D_TV` exists, a cross-solver wall-clock comparison to N=128 exists. Still no abstract, no conclusions, two of four models unused. |
| Novelty & positioning | narrow | **narrow** | Unchanged. The auto-scale result is a useful methodological control whose standalone novelty is not yet demonstrated. |
| Readability & writing | C+ | **C+** | Spelling substantially improved — zero misspellings across 772 lines — but a professional English edit is still required, and Figure 7's caption contradicts its own markers. |
| Reproducibility | C− | **D+** | **None of the three new headline experiments can be reproduced end-to-end from this repository.** Figure 14's plotting scripts are absent, Figure 7 has PDFs but no data, and the CEM validation has neither cache nor script. |

### The blockers, in order

1. **Figure 7 has no data, no cache and no plotting script in this repository**, and its methodology is under-specified (§6, N-B1). The report's headline solver comparison currently cannot be checked by anyone.
2. **Figure 7's prose contradicts the figure twice, and both versions are false** (N2); its caption specifies a marker convention the plot does not follow (N3).
3. **The TTE comparison is not yet a fair benchmark** — "matched hyperparameters" is not matched effort, and seven definitional items are missing (N-B1).
4. **F2's consequence is unresolved.** The report shows β_x does not control temperature under `auto_scale`; what the QPU experiments' actual β_eff *was* is therefore unknown and uncalibrated (F2).
5. **N1 — two incompatible ratios for the same figure**, 8–17× at L544 versus 7–27× at L563; the caches support L544. Trivial to fix, but it is a visible numerical contradiction.

---

## 2. Status of revision 3's findings

### F1 — CEM validation used the wrong reference family → **VERIFIED FIXED** *(confirmed)*

L432 now defines the ground truth as the marginal of the β-rescaled **joint**, `p_β(v) ∝ e^{−β a·v} Π_j 2cosh(β Θ_j)`, consistent with Eq. (13). The wrong family is gone everywhere: `grep` for `|\Psi|^{2\beta}`, "unbiased", "overestimate", "high-temperature" returns **zero** hits, so neither artefactual conclusion survives. The corrected RMSE — **0.107** (N=8), **0.112** (N=12) — comes with a qualitatively different, internally consistent bias description, corroborated by the regenerated figure (bias axis spans 0.00 to −0.10, negative throughout). The 480-draw arithmetic checks out.

*Residual:* the numbers cannot be recomputed from anything on disk (see §6). L432 says the saturated draw is excluded from the **RMSE**, the caption says from **panel (b)** — state one scope.

### F2 — `auto_scale` nullifies the β_x → β_eff mechanism → **PARTIALLY FIXED** *(confirmed)*

New §4.3.2 (L386–421) states the mechanism correctly and measures β_eff directly from QPU samples with `auto_scale` on and off. I verified both branches by calibrating the log axes of `dtv_autoscale_beta_N8.pdf`: the `True` branch sits at **2.78–2.91** (matching the stated ≈2.7–3.0) and the `False` branch runs 2.74 → 0.49, a parallel line a factor ≈4 above the ideal. This is an honest negative result, and it closes two other gaps at once.

**What it establishes, stated precisely:** *in the configuration tested* — N=8, one model, `Advantage_system6` (Pegasus), chain-free embedding — a uniform β_x rescaling does not control the sampling temperature when `auto_scale=True`.

**What it does not establish** *(this corrects revision 4, which over-generalised here)*: it does **not** show that every other QPU result in the report sampled at β_eff ≈ 2.8. Effective temperature depends on the instance, the coefficient scale, the solver, the embedding and its chains, the annealing schedule and the freeze-out point — D-Wave's own `freezeout_effective_temperature` documentation says as much, and instance dependence is the central point of Benedetti et al. (PRA 94, 022308). The correct statement is: **for every other QPU experiment the actual β_eff is unknown and uncalibrated.** That is a weaker claim but a more troubling one, because it applies to the sparsity and parallel-embedding results as well.

*Residuals.* (1) The unknown-β_eff caveat is nowhere propagated: §4.2 asserts at L328 that QPU TTE "is comparable to the classical MCMC samplers at the same size" without it. (2) L260 still states flatly that the β_x rescaling "is the origin of" β_eff, unqualified. (3) L390 attributes the residual to "a fixed offset set by the chip's own physical temperature" — an attribution the earlier audit warned against, and a multiplicative prefactor is not an offset. (4) The applied autoscale factor R is never reported, and L390's "native Pegasus biclique" should be reconciled with what was actually embedded.

### F3 — The sparsity study's central claim

- **(a)/(b) → OBSOLETE** *(confirmed)*. `pdftotext` on the figure lists four series — Metropolis, SA, persistent-chain Gibbs, Exact floor — with no QPU arm, and the prose now says "For budget constraints, we tested the sparse models only on classical hardware" (L563). This was a scope cut, not the budget-matched re-run. *Housekeeping:* the filename `..._qpu_vs_classical.pdf` and `cache_sparsity_ablation_qpu.json` are stale leftovers.
- **(c) spliced classical curve → VERIFIED FIXED** *(confirmed)*. The dense 288-parameter point is gone; `cache_sparsity_ablation_exact.json` now carries five keys including the native mask, so all four series share a left edge.
- **(d) → FIXED at L544, superseded by N1.** L544's numbers reproduce the caches to the digit; I recomputed the per-level ratios independently: **12.77×, 16.88×, 7.89×, 11.84× → span 7.9–16.9×**, matching "8 to 17 times".

### Major findings — 15 of 17 verified fixed

**Verified fixed** *(confirmed against current text, `report.aux`/`.log`/`.blg`/`.out`, or the rendered figures)*: **M1** (Eq. 13 sign convention, both CEM equations consistent) · **M3/M4** (Eq. 27 keeps only the antiperiodic sum with `J>0`, `h≥0`, PBC stated; re-verified against dense ED, agreement 9×10⁻¹⁶…4×10⁻¹⁴) · **M5** · **M6** · **M7** (`Σ` for the unregularised covariance; all four sites agree) · **M8** · **M9** (⟨s⟩ on the exact ED ground state; citation moved to `Troyer_2005`) · **M10** (26/26 `\autoref` targets resolve, zero `??`) · **M11** · **M12** · **M13** · **M14** · **M15** · **M16** · **M17** · **M18** (46 bookmarks decode, zero hyperref warnings).

**M2 — resolved better than recommended.** Code inspection showed neither textual description was accurate: the estimator pools over a whole batch of joint samples with **no clamping of `v`**. The manuscript now says so and Eq. (19) is a double sum. Consequence for this audit: `verify/cem_objective.py` models a single-condition estimator the code never implemented, so its 24.8 % saturation figure is a general note about single-condition matching, **not** a measurement of this implementation.

**M19 — fixed, but each fix exposed a latent defect.** Months, Richter's bracing and the `jaxGlossaryTerms` fields are correct and `bibtex` reports zero warnings. But publishing two previously-uncited entries revealed that reference **[5]** prints literal `{M}{P}{I}{P}{K}{S}` braces and **[15]** prints "Veloxq: A fast and efficient qubo solver" — the same `unsrt` case-folding bug M19 fixed for Richter. Reference **[6]**, the source of the entire CEM method, prints with no locator.

**Not fixed: 13 of 19 minors** — see Appendix A.

---

## 3. New findings in the material added since `973f11b`

### Blocking

**N-B1 — The TTE comparison is not yet a fair benchmark, and cannot be checked.** *(confirmed)* §4.2 rests on seven series compared under "matched hyperparameters" (learning rate 0.08, regularisation 0.05, 200 samples/iteration, 100 iterations). Identical sample and iteration counts are **not** comparable effort across Metropolis, SA, Gibbs, LSB, an FPGA and a QPU: per-iteration cost, mixing, and tuning sensitivity all differ, and VeloxQ is labelled "(SA, **untuned**)" inside the figure image. The section is missing, at minimum: raw times and per-seed trajectories; the rolling-average window length; the exact "drops below ε and stays there" criterion; **what is inside the QPU's measured time** (programming, embedding, queueing, network, readout, post-processing); the timeout definition and the method behind the "censored (extrapolated)" N=128 points; the statistical procedure for medians under censoring; and either per-solver tuning or a justification for one common protocol. **As it stands the figure does not justify a solver-performance comparison, even after N2 and N3 are fixed.**

**N-B2 — Figure 7's prose contradicts the figure twice, and both versions are false.** *(confirmed by decoding `tte_vs_n_eps_0p01.pdf`)* L328 says censoring begins "first for Gibbs … while FPGA and VeloxQ continue to reach ε = 0.01 throughout the tested range", then that "by N = 128 no solver reaches the tight target". In the panel: **FPGA and VeloxQ are themselves censored (0/20) at N=128** and annotated 12/20 and 19/20 as early as N=24–32; **LSB's marker is filled at N=128 with 4/20** (its line is dashed — the marker, not the line, carries the censoring information); and the earliest censoring anywhere is **Zephyr QPU at N=16 (5/20)**, not Gibbs.

**N-B3 — Figure 7's caption and markers are inconsistent, so censoring cannot be interpreted unambiguously.** *(confirmed)* The caption says hollow marks sizes where **at least one** seed was censored, but FPGA at N=32 ("12/20") and VeloxQ at N=24 ("19/20") are filled; hollow appears to mean 0/20. Fix whichever of caption or script is wrong.

**N-B4 — The headline speed claim rests on an undisclosed configuration and fails at the largest size.** *(confirmed)* "(SA, untuned)" appears only inside the figure image, never in the body, caption or hardware-configuration subsection. And "fastest by roughly two orders of magnitude" is unqualified: in the loose-target panel VeloxQ climbs to ≈7 s at N=128, above Gibbs (≈1 s) and LSB (≈5 s).

**N1 — Two incompatible ratios for the same figure.** *(confirmed)* 8–17× (L544) versus 7–27× (L563); the caches give 7.9–16.9×. Also `$7$-$27\times$` renders its separator as a minus sign.

### Substantive

**N5** — §4.2's title says "Time-to-solution" while it measures **TTE**; **TTS** is a different quantity formally defined by Eq. (1) 267 lines earlier. Rename to "Time-to-ε across solvers". · **N6** — `\epsilon`/`\varepsilon` collision: three meanings across two nearly identical glyphs, one a target *on* the other (L326 vs L302/L499/L544/L560 vs L656–658). · **N7** — "following the convention used elsewhere in this work" (L326) describes a convention that does not exist: three different marks for two concepts across Figures 7, 14 and 15b. · **N8** — Two different β_eff estimators share one symbol with no comment: TV-argmin (L376) versus KL-argmin (L398, L432), in sections whose whole point is to compare their results. · **N9** — §4.3.3's index `i` is the visible-unit index at L423 and the sample index at L425–429, with the visible index silently renamed to `l` at L429. · **N10** — Bias figures quoted on two incompatible aggregations presented as one: "−0.07 to −0.08" then "≈−0.19 at β_x=0.5" (L432), the first averaged over β_x, the second conditioned on it. · **N11** — L429's "lower-variance **in practice**" promises a head-to-head against single-condition CEM that the validation never runs. · **N12** — The Methods CEM paragraph (L212–221) now duplicates §4.3.3 in clashing notation (`c_j` vs `b_j`, two argmin styles, SRBM vs Boltzmann-machine framing); cut it to the pointer L211 already provides. · **N13** — Body says the Zephyr chip is the size constraint while caption and legend show both Pegasus and Zephyr (L326 vs L346).

### Cosmetic

See Appendix A.

---

## 4. Completeness

**Closed or advanced.** QPU β_eff is now measured (§4.3.2). A QPU `D_TV` now exists (L406) — though as a by-product of the auto-scale sweep, plotted against β_x rather than sampling effort, so it is not comparable with Figure 6, and the Sampling Quality section is still classical-only. A cross-solver wall-clock comparison now exists (§4.2), subject to N-B1. Sizes now reach **N=128** classically and 64 on the QPU, so the enumerable-range limit is gone, though the models remain exactly solvable.

**Still open.** No abstract, no Discussion, no Conclusions (zero grep hits in source and PDF; the question posed at L52 is never answered) · no data/code availability statement · `\date` unset, so the title page stamps the build date ("August 7, 2026") · LRTFIM and XXZ still appear in zero results, while L662 still justifies exact diagonalisation by invoking long-range interactions · the sparse-embedding section still does not test dense-with-chains versus native-sparse · CEM still never applied to the QPU, though L221 says it can be · no headline accuracy number for QPU-driven training at any N · parallel-embedding controls absent (whether `num_reads` was divided by `n_parallel`, chain-length and chain-break statistics, independence between copies) · numeric η, λ, CG tolerance and LSB settings unreported, the "sampling floor" defined only in captions, and **no table environment anywhere** · the framing contradiction (which hard-but-stoquastic class remains the target) unaddressed.

---

## 5. Novelty and positioning

Revision 3's assessment stands: the CEM validation is pre-empted by Kubo & Goto (arXiv:2512.02323); the sparse chain-free RBM is incremental against Park et al. (UCNC), Golubeva & Melko (PRB 105, 125124), Pilati & Pieri (PRE 101, 063308) and Marshall et al. (PRR 2, 023020); parallel embeddings are standard practice (Pelofske, Hahn & Djidjev, Sci. Rep. 12, 4499); and the sampling-quality benchmark sits in the territory of Berns, Rodrigues, Finocchio & Mentink, *Phys. Rev. Applied* 25, 024085 (2026). The residual open gap — an SB-class sampler with per-iteration effective-temperature correction inside an NQS/VMC loop — is narrow and inside one group's active programme. The defensible differentiator is the **mechanism**, not the hardware class. None of the missing citations listed in revision 3 has been added.

**On the auto-scale result** *(revision 4 overstated this; corrected)*: the mechanism follows directly from the documented definition of `auto_scale`, and the demonstration covers one RBM at one size on one solver with one embedding. It is a **valuable methodological control and a good case study** — and it is the kind of practical negative result that is worth reporting, since most work in this line leaves `auto_scale` at its default. But its standalone novelty and its generality across instances, solvers and embeddings have not been demonstrated, and whether it is already documented in the annealing literature was not surveyed. Treat it as a supporting contribution, not a headline. *(This paragraph is editorial judgement, not an audit finding.)*

---

## 6. Reproducibility — **D+**

**None of the three new headline experiments can be reproduced end-to-end from this repository.** *(confirmed by inventory)*

- **Figure 14 (sparsity).** Revision 4 stated that both plotting scripts are now committed. **That was wrong, and this audit should not have repeated an annotation without checking it.** The report repository contains exactly one experiment script, `scripts/dtv_autoscale.py`, plus this audit's `verify/*.py`; `plot_sparsity_ablation_floor.py`, `plot_sparsity_ablation_heatmap.py` and `exact_ansatz_floor.py` are in neither repository as checked out here. What *is* committed and verified is the data: five caches including `cache_sparsity_ablation_exact.json`, from which I independently reproduced every number in L544.
- **Figure 7 (TTE).** The report repository holds two PDFs and nothing else — no run JSONs, no cache, no script. A generating script (`scripts/viz/plot_tte.py`, reading per-run JSONs) exists in the implementation checkout, but that checkout is dated 2026-06-16, months before the figure, so whether it produces this figure is unknown.
- **Figure 9 (auto-scale).** `scripts/dtv_autoscale.py` is committed but is not a runnable artefact here: `_ROOT = Path(__file__).resolve().parent.parent.parent` resolves one level too high (to `Desktop`) for a file at `scripts/dtv_autoscale.py`, its docstring documents a `scripts/dtv/` location, it imports `src/` from the other repository, and neither its output JSON nor the checkpoint it consumes is committed. Its docstring also opens "A reviewer pointed out that…" and repeats the physical-temperature attribution flagged in F2 residual 3.
- **F1 (CEM validation).** Neither the experiment, the checkpoints nor a cache is present, so the corrected headline RMSE cannot be recomputed.
- **The implementation checkout is stale.** `/Users/bartek/Desktop/adiabatic-boltzmann` is at `2383dacf` (2026-06-16) and reports 69 commits behind its tracking ref — a comparison against a local ref, so without `git fetch` even that is not current. **Every code-side claim in this audit's history is therefore `cannot verify here`**; the fixes may be exactly as described.
- **Still open from before:** the seeding sentence (L708) describes `np.random.randint` feeding `jax.random.PRNGKey` while every cache key ends in one of five fixed seeds `{42, 123, 456, 789, 1234}` that appear nowhere in the manuscript; cache semantics remain undocumented (iteration count is `len(energy_history)`, the seed lives only in the key, key field 2 means target sparsity in one file and α in another, `E_final` is a re-evaluation differing from `energy_history[-1]` by up to 6 % of `|E_exact|`); no environment description; no availability statement.

---

## 7. Readability

**Genuinely improved.** Zero misspellings across all 772 lines including the new material; 33 `\autoref`s with 33 resolving targets and no `??`; all 46 PDF bookmarks decode cleanly; `bibtex` reports zero warnings; all 33 `\includegraphics` targets exist.

**But a professional English edit is still required** *(revision 4's "language is genuinely clean" conflated spelling with grammar, and contradicted this audit's own unfixed-minors list)*. Verified present: "the D-Wave's ability" and "The D-Wave's Quantum Annealers performance" (L51, L55) · "a initial driver Hamiltonian" (L140) · "a handful of highly probable sample configuration" (L296) · "In this chapter" in an `article` class (L586) · "Lanczos algorithm … only returns the matrix' lowest eigenvalue" (L663) · "For budget constraints" (L563) · plus the purpose sentence at L51.

**Structural, unchanged.** No abstract, no conclusions; §5 "Implementation" (methods) still follows §4 "Experimental Analysis" (results); the JAX tutorial and Appendix still read as thesis material.

---

## 8. What to do next

*(Ordering is judgement; the findings above are verifiable.)*

### P0 — the new experiments are not yet checkable or readable
1. **Commit Figure 7's run data and plotting script**, and specify the TTE protocol (N-B1): rolling-average window, the "drops below and stays there" criterion, what is inside the QPU's measured time, the timeout and extrapolation method, and the median-under-censoring procedure. Until then the headline comparison cannot be assessed.
2. **Rewrite L328 from the figure** (N-B2) and settle the marker convention in caption or script (N-B3).
3. **Disclose or drop "(SA, untuned)"**, and qualify "two orders of magnitude" with "at small N" (N-B4).
4. **State the β_eff situation correctly** (F2): keep the finding that β_x does not control temperature under `auto_scale`, and add that the other QPU experiments' β_eff is consequently unknown and uncalibrated — do not assert a value for them. Qualify L260 in place; replace "offset set by the chip's own physical temperature" with "a constant prefactor ≈4.1 in this configuration".
5. **N1**: reconcile 8–17× with 7–27×; rename §4.2 to "Time-to-ε across solvers" (N5).
6. Fix the two bibliography exposures and give reference [6] a locator.

### P1 — before any submission
7. Calibrate β_eff per experiment class (or run with `auto_scale=False` at a β_x calibrated **for that configuration**), which would also give the report its first temperature-correct QPU results and close CEM-on-QPU.
8. Commit the CEM-validation cache and script; pull the implementation repository so code-side fixes become checkable; add an environment description.
9. Add an abstract, a Discussion/Conclusions section answering L52, a data/code availability statement naming caches, solver IDs and the five seeds, a pinned `\date`, and an experimental-protocol table.
10. Either add LRTFIM/XXZ results or cut those subsections; add the missing citations; reframe the sparse and parallel-embedding work as method notes with their prior art; commission an English-language edit.

---

## Appendix A — cosmetic and low-priority items

**Unfixed minors from revision 3 (13 of 19).** Duplicate `\usepackage{graphicx}` (L7, L12) · stray `*` in the appendix divider · italic `$20\,\mu s$` and the document's single overfull box · `f(x^n)` / `q(x_n|x*)` slips in Eq. (12) · spurious "thermodynamic limit" · `σ_y` declared but absent from the equation it follows · SRBM never defined · Lanczos description · `D_TV` normalisation · LRTFIM Kac normalisation · coupler-type descriptions · the `\sqrt{}`-ansatz convention statement · `W_{ij}` vs `W_{ji}`, now spread across four equations plus the new code listing and disagreeing with L675's shape comment · the "solid markers" caption still contradicts its legend (the "hidden" swatch is an empty white rectangle).

**Cosmetic items in the new material.** "overtaking … to become the slowest" inverts the verb (L328) · "SAPI" used once, never expanded, and bare `h`/`J` reused for qubit bias and coupler strength (L388) · the code listing consumes `energies` without producing it (L393–399) · `LSB~+CEM` renders as "LSB +CEM" while the legend says "LSB (+CEM)" · reviewer-response register in the manuscript at L328 and in `scripts/dtv_autoscale.py`'s docstring · L542 points at the whole of Figure 14 for a claim only panel (b) supports · "representability" for "representational capacity" (L563) · Figure 11's caption is the only one without a terminal period, and "β_eff = 1.94 hugs the data" attributes to a value what the curve does · `\emph` only at L388 against 19 `\textit` · `\subsubsection{CEM}` the only bare-acronym heading · the four new CEM subfigures the only ones missing `\centering` · `\subcaption` vs `\caption` mixed inside subfigures · `D_TV` in four spellings (`D_{TV}` typesets as an italic product) and `β_eff` in two · four `~\cite` sites against six that butt against the preceding word · 21 lines with trailing whitespace and a three-blank-line run at L606–608.
