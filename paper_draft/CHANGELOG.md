# Paper draft changelog — team note

Not part of the manuscript. Records what was changed in `paper_draft/`, where each
change came from (evaluation PDF vs. audit doc — these are two different source
documents, see note below), and what was actually done or explicitly not done, and why.

**Sources, disambiguated:** `research_stay_report_evaluation.pdf` ("the evaluation")
reviews the research-stay report as a basis for a paper and proposes the
pooled-thermometry framing this draft follows. `audyt_cld_bg.md` ("the audit") is a
separate, independent line-by-line audit of `report.tex` with its own O1–O10 finding
numbers. Do not conflate the two — an earlier draft of this paper mislabeled an audit
finding as coming from the evaluation; that citation has been corrected in
`calibration.tex`.

---

### 2026-09-21 — Initial draft

Drafted the whole paper (`main.tex` + `sections/*.tex`) following the evaluation's
recommended 7-section structure and its "strongest paper hidden inside this report"
framing (pooled conditional thermometry + independently validated time-to-accuracy),
rather than the report's original broader/negative framing. Every claim the evaluation
flagged as needing new analysis or code was marked with a `\missing{}` placeholder
rather than silently dropped or asserted. Built Appendix `sec:code-gaps`, a file-and-line
inventory (T1–T8) of what supporting code does/doesn't exist in the implementation
repo, produced by an agent audit.

### 2026-09-21/22 — T3: TTE99 retry-cost statistic

**Source:** evaluation, main issue 1, *"The present TTE99 definition underestimates
retry cost"* — failed attempts are charged at the successful-seed time `T_r`, not the
full budget they actually consume; the sharp `20/20` vs. `19/20` distinction isn't
statistically supported by the underlying counts.

**Done:** explored a fixed-cutoff-τ reformulation, found it introduces its own
selection-bias problem (minimizing over a dense τ grid on the same sample being
evaluated), and **replaced the scalar TTE99 statistic entirely** with direct
error-vs-time reanalysis (`fig_error_vs_time_grid`, `reanalyze_tte.py`) — pure reanalysis
of already-archived per-seed histories, no new experiments. Restated the corrected
headline crossover claim (Sec. `limitations`) from real median crossing times: Pegasus
(0.47s) < FPGA (0.59s) < Zephyr (0.84s) < Gibbs (1.04s), all within ~2×, with overlapping
IQR bands — not the report's original "both QPUs overtake FPGA."

### 2026-09-22 — O2 (audit, not evaluation): matched classical-vs-QPU sampling benchmark

**Source:** the **audit**, finding O2, *"No matched QPU-versus-classical
sampling-quality benchmark... CEM is deployed on QPU samples but never validated on
them."* (Originally mis-cited in this draft as an evaluation item; corrected.)

**Done:** discovered the archived `kl_exact` field (exact-enumeration KL divergence
between each iteration's samples and the model's own Born distribution, logged for
N≤16 on both classical and QPU-driven runs) already answers this, unused. Built
`fig_kl_exact_solver_comparison` and `fig_kl_exact_cem_ablation` (`reanalyze_kl.py`) —
zero new experiments. Bonus finding: pooled CEM correction reduces this KL by ~4×
(Pegasus) and ~10× (Zephyr). **Marked O2 closed** in `calibration.tex`, with one caveat
noted: the audit also asked for β_eff to be reported alongside, which we did not
tabulate directly (we show CEM's downstream effect instead).

### 2026-09-22 — T1: conditional-MLE thermometry estimator vs. least-squares

**Source:** evaluation, *"The strongest paper hidden inside this report"* section —
proposes a conditional maximum-likelihood estimator as a theoretical strengthening of
the pooled least-squares CEM estimator, asks that it be compared against it.

**Done, in two stages:**
1. Implemented the MLE score equation and tested it on samples drawn at the model's
   own native β=1 (three saved checkpoints, N=8, h=1.0). Found both estimators unbiased,
   MLE ~15–20% lower variance once partially trained. Moved to an appendix,
   marked **preliminary** — modest effect, one cell, untested on real hardware.
2. Follow-up controlled test (this session): fixed a no-op bug in the original archived
   validation study's β_x sweep (its Gibbs sampler never actually varied the true β) by
   properly rescaling checkpoint parameters to generate genuine known-β samples across
   a wider range. Found least-squares has a **rare (~1.5%, 5/324) catastrophic failure**
   at high β (≥2.0) on well-trained networks — blows up to its search boundary; MLE
   showed zero such failures in the same test. See
   `fig_cem_residual_controlled_comparison.pdf` (shared log-log axes across all 6
   panels, at the author's request, so LS's outliers and MLE's tight cluster are
   honestly comparable on one scale).

**Decision: NOT adopted, and subsequently removed from the paper entirely
(2026-09-23).** Explicitly decided not to replace `β_LS` with `β_MLE` in any real
training run / not redoing this paper's experiments with it. Reasoning: low failure
rate, one synthetic cell only, the real pipeline's `beta_x` EMA update would likely damp
a single bad estimate rather than let it propagate, and no evidence this failure mode
ever occurred in any archived real run. Recorded as a project memory
(`project_mle_estimator_decision.md`). Since it plays no role in any experiment this
paper reports, the author asked to remove it from the manuscript altogether rather than
carry an unused estimator: deleted Sec. `cem-mle` (the derivation, Eq. cem-mle/score),
Sec. `cem-theory` (the open theoretical items, all MLE-specific), the appendix
`app:mle-check` validity check in full, the T1 row from the code-gap table, and every
mention in the abstract/intro/conclusion. The supporting figures/scripts
(`fig_mle_vs_ls_known_truth.*`, `fig_cem_residual_controlled_*.*`,
`plot_mle_residual.py`, `reanalyze_mle.py`) are kept in
`paper_draft/figures/reanalysis/` for reference but are no longer referenced anywhere
in the manuscript. Sec. `cem-ls` (the least-squares estimator actually used everywhere)
is untouched.

### 2026-09-23 — T5: QPU hardware-resource telemetry — **partially closed**

**Source:** evaluation, main issue 4, *"The reported power laws are not credible
scaling evidence"* — asks for physical-qubit count, chain length, chain-break
fraction, embedding success rate, and a programming/anneal/readout time breakdown per
$N$, instead of an unexplained four-point timing exponent.

**Done:** discovered `embedding_info` (qubit count, mean/max chain length) is already
logged in the archived result files for $N=8,32,64$ (both devices), unused — same
pattern as `kl_exact`/O2. $N=16$ is genuinely absent from every archived file (checked
multiple seeds), but closeable **offline**: both devices' live hardware-graph snapshots
are cached on disk (`embeddings/_hwgraph_{Advantage_system6,Advantage2_system1}_live.json`),
so re-running `minorminer.busclique` against that cached graph reproduces the same kind
of number with no QPU or network access at all (`analyze_embedding.py`). Added
Table~\ref{tab:resources} and one sentence to `resources.tex`: **Zephyr is cheaper than
Pegasus up to N=32, then crosses over — at N=64 (the size the corrected crossover claim
is made at) Zephyr needs more qubits (956 vs. 768) and longer chains (7.47 vs. 6.00)**, a
concrete hardware correlate of its worse showing there. No figure added to the
manuscript per author's request (table + sentence only); `fig_qpu_resource_scaling.*`
kept in `figures/reanalysis/` for reference.

**Still open** (genuinely needs a live QPU call, not reanalysis): chain-break fraction,
coefficient-rescaling range, embedding success rate, number of simultaneously available
embeddings, programming/anneal/readout time breakdown. Left as an explicit `\missing{}`
in `resources.tex` and noted in the T5 row of the code-gap table.

### 2026-09-22 — Novelty-positioning citations

**Source:** evaluation, novelty section — names a 2025 online-calibration paper
(arXiv:2307.09785v2) and a 2026 Physical Review E paper as narrowing this project's
novelty claim, without giving full bibliographic details.

**Done:** fetched and verified both papers via web lookup (titles/authors/venues
confirmed, not fabricated): Goto & Ohzeki, JPSJ 94, 034002 (2025); Kim, Gyhm & Park,
Phys. Rev. E 113 (2026). Added both to `references.bib` and tightened the introduction's
novelty paragraph to state the contribution more narrowly (the specific pooled/no-requery
construction and its MLE counterpart, plus a deliberately narrow empirical claim) rather
than "online calibration from training samples" in general, which both papers already do.

### 2026-09-23 — Numeric CEM residual analysis — investigated, NOT yet integrated

**Source:** evaluation, technical corrections — *"Figure 9 should report numerical RMSE,
relative error, bias, and boundary-hit frequency... rather than saying only that CEM is
'very close' to the exact estimate."*

**Done so far:** reanalyzed the archived 480-record `cem_validation_results.json`
(`reanalyze_cem_residual.py`, `plot_cem_residual.py`). Finding is more substantive than
a flat bias number: least-squares CEM shows a **systematic, value-dependent compression**
toward the middle of the tested β range (overestimates low β, underestimates high β,
consistent across training stages) — a mean/RMSE summary alone hides this since positive
and negative residuals cancel. **Not yet written into `calibration.tex`** — investigation
paused to build the follow-up MLE controlled-sweep test instead (previous entry). Still
open: decide how (or whether) to fold the compression-pattern finding into the paper.

### Editorial spot-check — no action needed

Checked our own draft against the evaluation's small technical-correction items
(σ_i^x vs. σ_i^xσ_j^x in the TFIM term, "Sorella" spelling, "sparsity rate" mislabeling,
consistent β_eff usage). All clean — this draft was written fresh rather than copied
from `report.tex`, so these specific slips were never introduced.

---

### Still open (not touched this session, or only partially)

- **T2** (independent frozen-checkpoint evaluator at N≥24): blocked — no checkpoints
  exist for the actual benchmark cells above N=16, and exact enumeration is infeasible
  there. `kl_exact` (see O2 above) gives partial evidence at N≤16 only.
- **T4** (h-sweep across the full N grid): still needs new QPU/classical runs.
- **T5–T8** (QPU hardware-resource telemetry, end-to-end timing, FPGA documentation,
  measured FPGA energy): unchanged from the original code-gap audit.
- The numeric CEM residual writeup (previous entry).
