# Revision history of `audyt_cld_bg.md`

## Revision 11 — 2026-08-25, verification pass; closed findings removed

Every finding of revisions 8–10 was re-checked against `report.tex` at `9917b34` (796 lines, 27 pages) — against the text and the bibliography, not against the author's annotations. **16 of 24 findings are verified closed and have been deleted from the audit**, leaving eight open items (O1–O8) plus a one-line record of what was closed and how.

The three post-audit commits (`5ab5210` "fixed audits findings", `a8d03fc`, `9917b34`) resolved every blocking finding except one, and did so substantively: the CV stopping rule was removed outright rather than re-tuned; the axis was relabelled sampler time with the SR/CG exclusion stated; the average sign was moved into the Marshall gauge with an explicit note that it vanishes by SU(2) symmetry otherwise; the misattributed citations were replaced with `Heisenberg_1928` and `{Sorella_1998,Sorella_2001}`; the parallel-embedding numbers were restated as total budget rather than time-to-plateau; the `dwave-neal` ambiguity was resolved by naming which implementation produced the results; and the bibliography grew from 16 to 29 entries, adding every foundational reference the audit had listed as absent.

Still open: the sparse-QPU contradiction (the refuting cache is still tracked in *this* repository even if it was removed upstream), the absent QPU sampling-quality measurement, the undisclosed ε-sensitivity behind a sign-flipping exponent, Figure 1(a)'s digitised provenance, the availability statement's missing commit hash, one incomplete bibliography record, `\appendix`/`\date`, and the two sampler clocks' boundaries.

---

## Revision 10 — 2026-08-18, after the second review round

`ocena_audytu_cld_bg_runda_2.md` is **right on five of its eight points, wrong on the one it calls a new blocker**. Everything was checked against the pinned implementation `a4b0f2006`, which was fetched before the network went down and inspected offline.

| Round-2 point | Verdict | Change |
|---|---|---|
| 1. B2 misdescribes the classical clock | **Correct — my error** | The pinned `Trainer` starts its timer immediately before `sampler.sample(...)` and stops immediately after; the energy meter is active only around that call, and the code comment says SR/CG/gradient work "isn't solver cost, so it's excluded". Both sides exclude SR/CG. **B2 rewritten**: the surviving defects are that the axis is labelled wall-clock *training* time while plotting *sampler* time (same for the energy panel versus "energy consumed to reach it"), and that device-reported `qpu_access_time` and host wall-clock around a classical call are different system boundaries presented as "directly comparable". |
| 2. B1 shows confounding, not proven artefact | **Correct** | Renamed to "confounded by a size-dependent stopping rule"; causal status marked `inference`; the decisive test is now named explicitly — recompute the committed histories under CV·√N < const or a direct oracle criterion and see whether the ordering and exponents survive. |
| 3. Forward-looking `plateau` window is a new blocker | **WRONG — refuted** | `compute_convergence_iter` returns `conv_iter = t − window + 2`, i.e. the 1-indexed **first** iteration of the plateau; `conv_iter − 1` is that same iteration 0-indexed, so the slice spans `t−window+1 … t` — exactly the triggering window. Verified for detection at t = 9, 15, 42. Recorded as **§3.9, examined and rejected**, with the arithmetic. |
| — consequence of 3 | **My error, withdrawn** | The same arithmetic kills revision 9's sub-finding that "the QPU medians correspond to 4–9 iterations, fewer than the 10 the rule requires": since `conv_iter` is the plateau's start, a TTE under ten iterations is expected. A legitimate residual is kept as one sentence — TTE is time-to-plateau-start, excluding the ten confirmation iterations, which flatters every series equally. |
| 4. B8 does not prove post-selection | **Correct** | The post-selection claim is dropped; B8 renamed "undisclosed threshold sensitivity" and now asks for a sensitivity table over all four (CV, ε) pairs. |
| 5. The pinned generator does not reproduce the shipped figure | **Correct — and escalated** | Verified: SHA-256 `4a56be72…` (report) vs `ded0bc94…` (upstream `_cv0.05_eps0.1`); the report's figure carries **9** fitted `∝ N^p` labels against **0** upstream; the pinned `fig10c` function contains no exponent fitting; and `__main__` calls eleven figure functions but neither fig10c nor fig10d. The artefact carrying the exponents that B1's claim rests on cannot be produced by any committed state. Folded into B8 as the decisive half. |
| 6. "69 commits during this audit" is wrong | **Correct — my error** | Verified: 13 commits between the two states this audit pinned; 82 since the stale local checkout it was first judged from. The 69 was the stale-checkout lag, and it was not "during this audit". M12 corrected. |
| 7. M9's language is too strong | **Correct** | Reframed: no logical contradiction between a TTS benchmark for rotation/factoring encodings and a TTE benchmark for RBM-VMC; the defect is that the two sit three pages apart with nothing separating their scopes and metrics. |
| 8. Wording | **Correct** | B5 "withheld experiment" → "unreported QPU arm"; M14 "print on every page" → "visible in the rendered PDF"; the history-purge procedure now warns to back up first, to expect `git filter-repo` to drop `origin`, and to rewrite every ref and tag. |

Net effect: one blocker rewritten on verified code, one causal claim downgraded, one sub-finding withdrawn, one proposed blocker refuted with arithmetic, one finding escalated with hashes, and four wording or numeric corrections.

---

## Revision 9 — 2026-08-18, corrections after `ocena_audytu_cld_bg.md`

The critique was adjudicated point by point against the files. **It is right on every factual point it raises**, and three of its findings are errors of mine that had reached a published revision.

| Critique point | Verdict | Change |
|---|---|---|
| 1. B1 (`auto_scale` contradiction) is already false | **Correct — my error** | Verified: L676 now reads `auto_scale` **disabled**, agreeing with L349. The contradiction was real in `6793638`, the snapshot the lenses audited, and was fixed by the merge that landed mid-audit. The blocker is **withdrawn**; §2 records the fix, and only the causal-claim criticism survives, as M16. |
| 2. Reproducibility assessed on too narrow a repository scope | **Correct — my error** | Fetched `iitis/adiabatic-boltzmann` and verified at `a4b0f2006`: `scripts/viz/paper_figures.py` contains `compute_validated_convergence_iter(...)` — the paper's own criterion — plus the fig10c/fig10d generators; **11 842 result files** (5 580 TFIM), each with `history`, `exact_energy`, `config` and timing; `plots/dtv_autoscale/dtv_autoscale_N8_h1.0.json`; and a `requirements.txt` (unpinned). Grade raised **D+ → B−**. What survives is narrower: no commit hash in the availability statement, unpinned versions, no QPU access dates. |
| 3. Material from `final changes` overlooked | **Correct — my error** | Verified: affiliation at L41–44; protocol (TFIM, h=0.5, lr, reg, samples, iterations, **seeds 0–19**) at L678; LSB's δ/γ/σ⁻² and every classical sampler's mixing parameters in `tab:classical_sampler_params`. Completeness raised **B− → B**. M4 narrowed to "stated 130 lines from the figure, hidden-unit count still missing"; M13 narrowed to an internal inconsistency. |
| 4. The energy finding assumed a QPU comparison | **Correct** | L544 states plainly that the QPUs are omitted "because no API exposes per-job energy draw". Reframed: the defect is that the **abstract claims superiority over quantum samplers on a metric with no quantum number**, plus the FPGA's 45 W assumed power draw — not an asymmetric measurement. |
| 5. Some `confirmed` labels are inference | **Correct** | Downgraded: the ≈2.8× CV factor is marked an extrapolation with its assumption stated; the iteration-count arithmetic marked inferred from marker positions; "the record was invented" became "the source does not support the claim; the record's origin cannot be traced", with an explicit request that the author check it; the "every other size" reading softened to a coverage limitation, since the text does give the correct explicit set. |
| 6. B5/B6 belong above bibliography items in P0 | **Correct** | Priorities restructured into three P0 groups — history purge, then methodology (scaling claim, clocks, censored estimator, ordering, withheld arm, Marshall figure), then attribution and figures. |

**New in this revision, found while verifying point 2:** the two thresholds defining the benchmark were swept. The generator defaults to `epsilon=0.01`, and upstream holds five fig10c variants over cv ∈ {0.03, 0.05} × ε ∈ {0.01, 0.1}; the paper reports one cell — the loosest on ε — without mentioning the others, and the figure was renamed on copy in a way that strips the `_cv{…}_eps{…}` suffix identifying which variant it is. Filed as **B8**, compounding B1.

Both repositories are now pinned in the audit header, since the implementation repository advanced 69 commits during revision 8 alone.

**Process note:** revision 9 was briefly written into the implementation repository by mistake — a `cd` in an earlier command had persisted as the shell's working directory. The file was moved to the report repository and the implementation checkout left clean; no commit was made there.

---

## Revision 8 — 2026-08-18, full re-audit

Not an update but a fresh audit: eight independent lenses (physics/mathematics, the diff since revision 7, the time-to-ε experiment, completeness, figures-versus-claims, bibliography and citation coverage, reproducibility, editorial/LaTeX) over commit `6793638` (734 lines), reconciled and de-duplicated. The branch moved during the audit — the incoming commit `0d846c2` ("final changes") took the file to 777 lines — so every surviving finding was re-anchored to the current text by grepping its quoted string.

**Structure changed.** The document is reorganised around *what blocks submission* rather than around the previous finding IDs: §0 for a non-manuscript issue, §1 with a blocker list, §2 for what is now good and should not be disturbed, §3 for the eight blocking findings in detail, §4 for majors grouped by area, then completeness, novelty, editorial and priorities. Previous IDs (F1–F3, M1–M22, N1–N15, N-B1–N-B4) are retired; their content survives where still true.

**Fixed since revision 7, verified:** bibliography mechanics (DOIs print and link — 52 `/URI` annotations, all 16 references linked, all URLs live, case folding completely defeated, journals unified, zero bibtex warnings, all ten DOIs checked against Crossref); the weight-matrix orientation; the time-to-ε protocol (oracle-free CV stopping rule, explicit validation-against-truth censoring, honest matched-hyperparameter disclaimer, stated QPU timing basis, justified N=128 omission); propagation of the β_eff caveat into the TTE section; CEM now applied to QPU samples; the unused models cut and the stale long-range justification removed; abstract, Conclusion and availability statement added; the exact TFIM closed form re-verified against dense ED.

**The dominant problem moved.** It is no longer specification but *claims versus evidence*: the solver-ranking sentence is false against its own decoded figure (SA is the slowest series at N≥16, not second-fastest); the abstract and Conclusion claim a strict FPGA win "at every size tested" that the body contradicts at N=64; "we tested the sparse models only on classical hardware" is contradicted by the repository's own committed QPU cache; and the manuscript states two mutually exclusive `auto_scale` settings for the same QPU work — the setting its own §4.3.2 shows determines β_eff.

**New this revision:** a private bank document found committed in `figures/` on a public remote (§0); two citations that do not support their claims (the Heisenberg model's only reference never mentions Heisenberg and its bibliography record is invented; SR is credited to a paper whose abstract says SR was introduced earlier); Carleo & Troyer absent from the whole document; the average sign identically zero by SU(2) symmetry for the models it characterises; the TTE median conditioned on success; two clocks on one axis declared comparable; the loosened ε=0.1 target undisclosed; and the deletion of the repository's only experiment script.

**Also corrected:** the five `verify/*.py` scripts committed by earlier revisions are pinned to line numbers that no longer exist and one prints a statement that is now false — flagged as M22 for update or deletion.

---

## Revision 7 — 2026-08-07, bibliography finding added

Added **N15**, a substantive finding on bibliography consistency, verified against `bib.bib` and `build/report.bbl`: nine `doi` and ten `url` fields are present but `unsrt` prints neither, so with `hyperref` loaded the only three links in the reference list belong to the blog post, the lecture notes and the JAX documentation while every peer-reviewed source is unlinked; `eprint`/`archiveprefix` are dropped too, leaving Kubo & Goto without any locator; the same journal is spelled "Phys. Rev. Appl." in one entry and "Physical Review Applied" in another; four articles print volume and issue with no page or article number; date granularity varies three ways; `unsrt`'s case folding is pervasive rather than limited to the two entries M19 patched; and entry types, author-name conventions and one brace-protected URL are inconsistent. M19's paragraph now points at N15 as the systemic version of its symptoms, and P1 gained item 13 — rebuild on a DOI/arXiv-aware style before adding the missing citations, so new entries are written once in the final convention.

---

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
