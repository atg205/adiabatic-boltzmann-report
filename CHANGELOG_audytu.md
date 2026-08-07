# Revision history of `audyt_cld_bg.md`

## Revision 6 — 2026-08-07, final consistency pass

Revision 6 resolves the remaining issues identified after revision 5:

- F1 now separates the confirmed reference-family correction from RMSE/bias values that are only internally consistent with the committed figure and cannot be reproduced from the available artefacts.
- M2 no longer presents unavailable code inspection as current evidence; the pooled implementation is marked `cannot verify here` unless an exact commit and path are supplied.
- F2 now says that β_eff for other QPU experiments is not established or reported, and no longer applies the temperature caveat to the classical-only sparsity ablation.
- The `W_{ij}`/`W_{ji}` transpose inconsistency was elevated from a minor to substantive finding N14 and added to P0.
- N-B1 now distinguishes confirmed missing disclosures from methodological judgement; common VMC settings are no longer described as a requirement for "matched effort" in a wall-clock benchmark.
- The unsupported claim that most related work leaves `auto_scale` at its default was removed.
- Temperature calibration and CEM-on-QPU are now separate recommended experiments.
- Fragile finding totals and the `table`-environment complaint were removed; Appendix A was pruned of low-value style counts.
- The audit header no longer embeds a repository HEAD that becomes stale whenever the audit itself is committed.

---

## Revision 5 — 2026-08-07, correcting revision 4 after a reviewer critique

The critique in `uwagi_do_audytu_cld_bg.md` was adjudicated point by point against the files. **It is right on all seven of its correction points**, two of which were real errors of mine and two internal contradictions. Applied:

| Critique point | Change |
|---|---|
| 1. β_eff ≈ 2.8 must not be generalised | **The most important correction.** Revision 4 wrote that "every other QPU result sampled at β_eff ≈ 2.8". Figure 9 measures one configuration (N=8, one model, Pegasus, chain-free); β_eff depends on instance, coefficient scale, solver, embedding, chains, schedule and freeze-out. F2 now says only that β_x does not control temperature under `auto_scale`, and that **the other experiments' β_eff is unknown and uncalibrated** — weaker, but more troubling, since it applies to the sparsity and parallel-embedding results too. The "re-run at β_x ≈ 4.1" recommendation was likewise narrowed to "calibrated for that configuration". Ironically revision 3's own F2 Fix paragraph had warned against exactly this inference. |
| 2. auto-scale novelty overstated | §5 now calls it a valuable methodological control and case study whose standalone novelty and generality are undemonstrated, explicitly labelled as editorial judgement rather than an audit finding. |
| 3. False positive in Reproducibility | **My error.** Revision 4 repeated the author's annotation that Figure 14's plotting scripts are committed, without checking. Verified: the report repository contains exactly one experiment script (`scripts/dtv_autoscale.py`) plus this audit's `verify/*.py`; the sparsity scripts are in neither repository as checked out. Also added: Figure 7 has two PDFs and no data/cache/script here, and `dtv_autoscale.py` is not runnable (`_ROOT` resolves one level too high, imports `src/` from the other repo, no output committed). Grade lowered **C− → D+** with the explicit statement that none of the three new headline experiments is reproducible end-to-end. One nuance the critique missed: `scripts/viz/plot_tte.py` *does* exist in the implementation checkout, but that checkout predates the figure by two months. |
| 4. "Language is genuinely clean" is false | Corrected to "spelling substantially improved; a professional English edit still required", with all seven cited grammar errors verified present. Revision 4 had contradicted its own unfixed-minors list. |
| 5. P0 priorities wrong | Reordered: Figure 7's missing data and under-specified methodology first, then the false sentences and marker caption, then the β_eff statement, then N1 — matching the Summary, which had already called Figure 7 the blocker while P0 led with N1. |
| 6. TTE methodology under-criticised | Promoted to **N-B1**, a blocking finding: "matched hyperparameters" is not matched effort across MCMC/SA/LSB/FPGA/QPU, and seven definitional items are missing (rolling-average window, the stay-below criterion, what is inside the QPU's measured time, timeout and extrapolation method, median-under-censoring procedure, per-solver tuning). Conclusion added: the figure does not justify a solver-performance comparison even after N-B2/N-B3 are fixed. |
| 7. Minor inaccuracies | Header verification changed to `git log -1 --format='%h' -- report.tex` (repository HEAD moves independently — it is `634bb39` now, and was already past the `e2705c2` the critique quoted). "LSB is drawn solid" → the *marker* is filled, the line is dashed. "Figure 7 cannot be decoded" → "caption and markers are inconsistent, so censoring cannot be interpreted unambiguously". "69 commits behind" now noted as relative to a local tracking ref, unverified without `git fetch`. N14 split by severity. |
| Style | Restructured per the critique's advice: a five-item blocker list up front, new findings split into blocking / substantive / cosmetic, and the cosmetic pile moved to Appendix A. The "24 new defects" headline is re-cut as 5 blocking / 9 substantive / 10 cosmetic. |

---

## Revision 4 — 2026-08-07, re-verification against commit `5bc5a64`

Revision 3 audited `973f11b` (712 lines). Over the following ten days the author fixed most of it, annotated this audit inline with `(FIXED)` notes, and added two subsections the audit had never seen. Revision 4 **re-verified every claimed fix independently** — none was taken on trust — using `sed`/`grep` on the live file, `build/report.aux`/`.log`/`.blg`/`.out`, the committed JSON caches, dense exact diagonalisation, and pixel-level decoding of the rendered PDFs.

**Scoreboard on revision 3's 26 in-scope findings: 20 verified fixed, 2 legitimately obsolete (F3 a/b), 2 partially fixed (F2, F3d), 1 not fixed, 1 fixed in a way that introduced a new contradiction.** No `(FIXED)` annotation was false — an unusually good record. The ~136 inserted lines carry **24 new defects**, 14 of them in the newest subsection.

### What changed in this revision

- **F1 → verified fixed.** The corrected ground truth is exactly the marginal of the β-tempered joint; the wrong family is gone everywhere (zero grep hits for `|\Psi|^{2\beta}`, "unbiased", "overestimate", "high-temperature"); the new RMSE 0.107/0.112 is accompanied by a qualitatively different, internally consistent bias description, corroborated by the regenerated figure.
- **F2 → partially fixed, and reclassified.** The author turned the finding into an experiment (new §4.3.2) that measures β_eff on hardware with `auto_scale` on and off; I verified both branches by calibrating the figure's log axes. The residual is no longer the diagnosis but its *propagation*: the report establishes that every other QPU result sampled at β_eff ≈ 2.8 rather than the target 1, and then never carries that anywhere. Two smaller residuals: L260 still states the refuted claim unqualified, and L390 makes exactly the physical-temperature attribution revision 3 warned against.
- **F3 → (a)/(b) obsolete by scope cut, (c) fixed, (d) fixed but superseded by new finding N1** (8–17× at L544 versus 7–27× at L563 for the same figure).
- **Twenty-four new findings (N1–N14)**, the serious cluster in §4.2 "Time-to-solution across solvers": its prose contradicts its own figure twice and both versions are false, its caption specifies a marker convention the plot does not follow, its headline speed claim rests on an undisclosed "(SA, untuned)" configuration visible only inside the figure image, and its title collides with the TTS metric Eq. (1) formally defines.
- **Three completeness gaps closed** by the new material: QPU β_eff measured, a QPU `D_TV` now exists, and a cross-solver wall-clock comparison to N=128 now exists. Grades moved: correctness B− → B, completeness C → C+.
- **New reproducibility finding:** the implementation repository on this machine (`/Users/bartek/Desktop/adiabatic-boltzmann`, HEAD `2383dacf`, 2026-06-16) is 69 commits behind its remote and contains none of the scripts the fix annotations cite, so every code-side claim is `cannot verify here`. Also, F1's corrected headline numbers cannot be recomputed from anything on disk.
- **Corrections to this audit's own earlier claims:** `verify/cem_objective.py`'s 24.8 %-saturation figure models a single-condition estimator the code never implemented (M2 was resolved by code inspection showing the estimator pools over a whole batch with no clamping), so it is now labelled a general note rather than a measurement of this implementation. Revision 3's line and equation numbers were superseded wholesale; a translation table is now in the audit header.

---

## Revision 3 — 2026-07-28, in response to `uwagi_do_audytu_cld_bg.md`

The reviewer critique was adjudicated point by point, independently rather than by deference: **right on five points (1, 3, 4, 5, 7), partly right on two (2, 8), one out of scope (6, literature — accepted and acted on), and partly right on the last (9)**. It was also wrong once — and wrong by agreeing with the audit.

### Accepted and applied

| Critique point | Change |
|---|---|
| 1. "mismatch alone explains the entire RMSE" too strong | F1 restated as *can produce error of this magnitude*, with the measured instance-dependence (RMS 0.008–0.19 across weight draws) and the observation that the reported RMSE lying *inside* that span shows a random-weight proxy overstates the effect. Script shipped: `verify/cem_family.py` (fixed seed). |
| 2. Eq. (20) "argmin is ill-posed" is wrong | Withdrawn. The critique's algebra is correct — the population risk is `Var(h_j) + (m_j(β₀) − m_j(β))²`, so the single-sample objective is a consistent M-estimator (verified: median β̂ → β₀ at N_h = 256). Replaced by M2: an inconsistent *description* across Eqs. (10)/(19)/(20) and Fig. 11a, plus a quantified boundary-saturation mechanism offered as plausible, not proven. |
| 3. Parity criticism over-generalised | Split by regime in M3: for `h < J` the periodic sum equals the lowest odd-parity state exactly (10⁻¹⁴); only for `h > J` does it fall `2(h−J)` below it. |
| 4. `auto_scale` fix oversimplified | F2's fix no longer claims β_eff reduces to the device's physical temperature; it now lists the programmed energy scale, `B(s)`/freeze-out, annealing dynamics, embedding and chains, analog error and non-Boltzmann deviations, and points at `freezeout_effective_temperature`. |
| 5a. "dotted line" caption | Downgraded from "identifies the wrong one" to **ambiguous** (M13). |
| 5b. "across the full sparsity range tested" | **Objection dropped.** The ablation caches contain only the four masks 0.5586–0.8789 and no dense point, so the phrase is accurate for that ablation. |
| 6. Missing literature | Berns, Rodrigues, Finocchio & Mentink, PRApplied 25, 024085 (2026), arXiv:2504.18359 verified in every field and added to §4.1 as prior art for the *sampling-quality* section — closer to what the report already did than to its proposed future work. §4.2 reframed from "open frontier" to "narrow gap inside one group's active programme" (Mentink co-authors both Berns and Chowdhury; Berns' only citation is Chowdhury). Also added: an SB/CIM-class sampler already driving RBM/DBN learning in PRApplied (DOI 10.1103/6c63-cmgy, Mar 2026) and Goto & Ohzeki, JPSJ 94, 034002 (2025). |
| 7. Seeding sentence credited too generously | Moved to §6 as a gap, and sharpened: every cache key ends in one of five **fixed** seeds `{42,123,456,789,1234}`, none of which appears in `report.tex`, so L647's `np.random.randint` claim contradicts the committed data. |
| 8. Inconsistent severity levels | Unified: three critical findings F1–F3 named identically in the summary, the body and the recommendations; everything else is M1–M19 (major) or §2.4 (minor). The old C5 (broken Eq. 8) became M5; the old C2 (CEM sign) became M1 with an explicit "raise to critical if the code shares it". |
| 9. Low-value minors | Dropped: missing `inputenc`, `\bibliography` before `\bibliographystyle`, "no `table` environment" as a reproducibility gap. "Needs 40–60 references" replaced by a list of missing literature *categories*. |
| Style | Confidence labels (`confirmed` / `strong inference` / `requires code inspection`) on every finding; Finding–Evidence–Impact–Fix structure for F1–F3; §7 explicitly flagged as mixing audit findings with expert judgement; revision history moved out of the audit into this file. |

### Where the critique was wrong

**The Fig. 12b axis label is correct.** Both revision 2 of the audit and the critique (§5) asserted that "Energy error per spin |ε|/N" is erroneous. Decoding the plotted markers and dividing by `|E_exact|/N = 1.27529` reproduces the committed cache means to ratio 1.00000 on all nine points, so the axis is right and the *prose* is what does not match: L484 quotes plain relative errors, which differ from the plotted quantity by a factor 1.275 and therefore cannot be located on the figure. Deleting the "/N", as both documents proposed, would have made the figure wrong. Now M12.

**Point 2 over-corrects.** The critique asked that the saturation attribution be dropped entirely. There is a rigorous degeneracy — `F(β)` is monotone whenever every observed `h_j` agrees in sign with `Θ_j`, so a bounded optimiser returns its bound, which at the report's own operating point (|Θ| up to ≈3, β_eff = 1.94) fires on ≈24.8 % of draws at `N_h = 16`. It is legitimate as a *plausible* mechanism. What is not legitimate is "almost certainly", because the same simulation refutes the literal single-sample reading: it predicts 120–200 saturated draws out of 480 against the 1 reported, consistent with ≈16–30 pooled draws and with Fig. 11a's "binned average" legend.

### Findings neither document had

1. **L484's floor numbers contradict the figure.** The plotted floor is 1.05/1.48/3.45/2.41 % per spin (0.82/1.16/2.70/1.89 % relative) — rising 3.3× and peaking at the third mask — not "roughly flat at 1.1–1.8 %"; and "five to fifteen times larger" is exceeded at sparsity 0.682 (16.9×). Now F3(d).
2. **Fig. 12b's classical curve splices two experiments.** Its sparsity-0 point is a dense 288-parameter biclique RBM from `cache_full.json`, joined to four coupler-pruned Zephyr masks from a different cache across a 0.55-wide gap with no data and no QPU or floor counterpart — while a comparable classical native-Zephyr point at sparsity 0.426 (3.28 % relative error) sits unplotted in the same cache. Now F3(c).
3. **The exact-ansatz floor has no committed cache, and no plotting script is committed at all** — so the one element of the sparsity study this audit rates genuinely new is the only arm a reader cannot reproduce. Now §6.
4. **At matched budget the QPU arm wins.** Budget deficits are 2.03×, 1.09×, 1.93×, 11.28×; at the two levels where they are comparable the QPU beats classical (8.4 % vs 10.5 %, 9.6 % vs 19.6 %). The "extra hardware penalty" claim has no support anywhere budgets are comparable — stronger than revision 2's "indistinguishable from a deficit". Now F3(b).
5. `min(energy_history)` beats the reported `E_final` in 110 of 120 cache records, making M6's point about downward-biased minima concrete.
6. Trivial slip corrected: the 12.5 M-pair parity scan began at h = 10⁻⁶ and so never included h = 0 exactly, where the two sector sums coincide.

---

## Revision 2 — 2026-07-28

Rewritten against the correct file after discovering that revision 1 described a stale revision. Introduced the CEM-family finding (F1), the `auto_scale` finding (F2), the budget-matching finding (F3), the six pre-empting prior-art items, and the withdrawal of revision 1's Jordan–Wigner criticisms.

## Revision 1 — 2026-07-28 — **invalid**

Described commit `9194802` ("jax part", 590 lines) rather than the working tree, because the file-reading tool returned the pre-`git pull` content. That revision was seven commits and 408 changed lines out of date.

Triage of its 122 claims against the real file: **60 still valid, 47 already fixed in the manuscript, 6 never true of any revision, 5 needing renumbering, 0 unverifiable.** Equation numbers were wrong from Eq. (8) onward.

Never true of any revision: "591 lines" (712), "16 pp." (21), "line numbers refer to `973f11b`", "no D-Wave data at all", "the CEM subsection is empty", "no error bars, seeds or repetition counts anywhere".

Already fixed in the manuscript before revision 1 was written: the TFIM Hamiltonian (σᶻ → σˣ), the title spelling, the Φ/Ψ ansatz contradiction, the β_eff = 1/β_x derivation, the entire Jordan–Wigner section (rewritten, cited to Dziarmaga_2005, numerically verified — so revision 1's factor-2 and parity criticisms of the E₀ *value* were withdrawn), the Marshall-theorem overclaim, the caption/figure mismatch (resolved by deleting the figure), "best run" selection (now median with IQR), the empty CEM subsection, the Kubo & Goto attribution gap, the LSB subsection nesting, and 8 of 16 spelling items.

**Process lesson, now built into the audit:** pin the commit hash, line count and page count in the header, and state the one-line check (`wc -l`, `sed -n '91p'`) that detects a stale read before any finding is written.
