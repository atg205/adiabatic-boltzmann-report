# Audit: *Quantum Variational Algorithms on Adiabatic Quantum Computing Devices* (`report.tex`)

**Target:** `report.tex` at commit **`5bc5a64`** ("added dwave beta scaling section") — **772 source lines, 23 compiled pages, 32 numbered equations, 15 figures**. Confirm with `wc -l report.tex` (→ 772), `sed -n '772p'` (→ `\end{document}`), `git log --oneline -1` (→ `5bc5a64`). Equation and figure numbers are anchored to `build/report.aux`.

**Revision 4** (2026-08-07). Revision 3 audited commit `973f11b` (712 lines); since then the author has fixed most of it and added two new subsections. **This revision independently re-verified every claimed fix** — none was taken on trust — and audits the new material for the first time. Full history in [`CHANGELOG_audytu.md`](CHANGELOG_audytu.md).

**Verification scoreboard against revision 3.** Of the 26 findings in scope: **20 verified fixed, 2 legitimately obsolete, 2 partially fixed, 1 not fixed, 1 fixed in a way that introduced a new contradiction.** No `(FIXED)` annotation was found to be false. Separately, the ~136 inserted lines carry **24 new defects**, concentrated in the newest subsection.

> **Numbering has shifted.** Revision 3's line numbers no longer apply. Equations: old (8)→(8) at L145, (10)→L214, (13)→L242, (16)→L256, (20)→**(19)** at L426, (28)→**(27)** at L655. Figures: old "Fig. 9"→**Figure 5**, "Fig. 12"→**Figure 14**, "Fig. 13b"→**Figure 15b**. New: **Figure 7** (time-to-ε), **Figure 9** (auto-scale).

**Reproduction scripts** in [`verify/`](verify/): `cem_family.py` (F1's mechanism), `cem_objective.py` (M2), `tfim_e0.py` (§2.1 exact solver, inert `min()`, parity regimes, J<0 failure), `cache_budget_stats.py` (all cache-derived numbers).

**Confidence labels:** `confirmed` (verified numerically, against a build artefact, a committed cache, or by decoding the figure), `strong inference`, `cannot verify here`.

---

## 1. Summary

| Dimension | Rev. 3 | Now | Verdict |
|---|---|---|---|
| Physics & math correctness | B− | **B** | F1 fixed at the source; the exact solver, ansatz, SR/CG and sign conventions are now sound. What remains are claims in new prose that contradict their own figures. |
| Completeness (promise vs delivery) | C | **C+** | Three formerly-critical gaps closed by two new experiments: QPU β_eff is measured, a QPU `D_TV` exists, and a cross-solver wall-clock comparison to N=128 now exists. Still no abstract, no conclusions, and two of four models unused. |
| Novelty & positioning | narrow | **narrow** | Unchanged, but the auto-scale negative result is a clean, citable calibration contribution the report should claim explicitly. |
| Readability & writing | C+ | **C+** | Language is now genuinely clean (a dictionary pass over all 772 lines finds zero misspellings) and cross-references are healthy — but Figure 7 cannot be decoded from its own caption, and its surrounding prose is factually wrong about it. |
| Reproducibility | C− | **C−** | The sparsity floor's cache and both plotting scripts are now committed. But F1's headline numbers cannot be recomputed from anything on disk, and the implementation repository on this machine predates every fix. |

**What is now blocking.** Not the physics. Three things: (i) the new time-to-ε subsection makes statements its own figure contradicts and specifies a marker convention the figure does not follow, so the section's headline comparison is currently unreadable; (ii) F2's finding is measured but **quarantined** — the report establishes that every other QPU result sampled at β_eff ≈ 2.8 instead of the target 1, then never carries that anywhere; (iii) the paper still has no abstract, no conclusions, and no data-availability statement.

---

## 2. Status of revision 3's findings

### 2.1 Critical findings

---

**F1 — CEM validation used the wrong reference family. → VERIFIED FIXED.** *(confirmed)*

L432 now defines the ground truth as the marginal of the β-rescaled **joint**, `p_β(v) ∝ e^{−β a·v} Π_j 2cosh(β Θ_j)`, which is exactly right and consistent with Eq. (13). The wrong family is gone everywhere: `grep` for `|\Psi|^{2\beta}`, "unbiased", "overestimate", "high-temperature" returns **zero** hits in all 772 lines, so neither of the two artefactual conclusions survives. The corrected numbers — RMSE **0.107** (N=8) and **0.112** (N=12), replacing 0.148/0.153 — are accompanied by a qualitatively different and internally consistent bias description (small, consistently negative, roughly flat across training rather than shrinking). Independently corroborated by the regenerated figure: `cem_validation_bias.pdf`'s y-axis spans 0.00 to −0.10, negative throughout with no shrink toward zero, and `cem_validation_calibration.pdf` carries a legend entry "N = 12 (hit search bound)" matching the excluded draw. The 480-draw arithmetic still checks out.

*Residual (minor).* Two small things. The RMSE values cannot be recomputed on this machine — no `cem_validation` cache or generating script exists in either repository. And L432 says the saturated draw is excluded from the **RMSE**, while the caption says it is excluded from **panel (b)**; state one scope.

---

**F2 — `auto_scale` nullifies the β_x → β_eff mechanism. → PARTIALLY FIXED; the finding is measured but quarantined.** *(confirmed)*

The response exceeded what was asked. New §4.3.2 (L386–421, `sec:autoscale`) states the mechanism correctly, then **measures β_eff directly from QPU samples** with `auto_scale` on and off on a chain-free Pegasus embedding: with `auto_scale=True`, β_eff is flat at ≈2.7–3.0 across a 5× range of β_x; with `auto_scale=False` it tracks ≈4.1/β_x. I verified both branches by calibrating the log axes of `dtv_autoscale_beta_N8.pdf` (208 px/decade, β_eff=1 at y=141): the True branch sits at **2.78–2.91** (so "≈2.7–3.0" is accurate) and the False branch runs 2.74 → 0.49, a parallel line a factor ≈4 above the ideal. This is an honest, well-scoped negative result and it simultaneously closes two other gaps (QPU β_eff measured; a QPU `D_TV` now exists).

*Four residuals, in priority order.*

1. **The consequence is quarantined.** L390 concedes that "wherever β_x was varied for QPU-sampled runs, it had no effect on the actual physical sampling temperature" — i.e. every QPU-sampled result in the report was drawn at β_eff ≈ 2.8 while L376/L418 state the VMC target is β_eff = 1, roughly 3× the intended temperature. That is never propagated: the time-to-ε subsection asserts at L328 that QPU TTE "is comparable to the classical MCMC samplers at the same size" with no such caveat, and Figure 15 carries none either. Either re-run with `auto_scale=False` at the calibrated β_x ≈ 4.1, or add an explicit limitation sentence wherever QPU samples are used.
2. **L260 still states the refuted claim.** Unchanged from the audited revision: "`a, b, W` are rescaled by a common factor β_x before being programmed onto the device; **this rescaling is the origin of** the effective inverse temperature β_eff". Only a forward reference was added. Qualify it in place.
3. **L390 makes exactly the attribution revision 3 warned against**, calling the residual "a fixed offset set by the chip's own physical temperature". β_eff also depends on the programmed energy scale, `B(s)` and the freeze-out point, embedding and chains, and analog control error. Also: 4.1/β_x differs from 1/β_x by a multiplicative **prefactor**, not an offset.
4. **The applied autoscale factor is never reported**, and the embedding is described at L390 as a "native Pegasus biclique" while the run appears to use a sparse hardware subgraph — check and reconcile.

---

**F3 — The sparsity study's central claim was contradicted by its own data.**

- **(a) unmatched budgets, (b) QPU wins at matched budget → OBSOLETE.** *(confirmed)* Verified against the artefacts, not the annotation: `pdftotext` on `sparsity_ablation_qpu_vs_classical.pdf` lists exactly four series — Metropolis, SA, persistent-chain Gibbs, Exact floor — with no QPU series, and no QPU-vs-classical claim survives in the prose ("For budget constraints, we tested the sparse models only on classical hardware", L563). This was a scope cut, not the budget-matched re-run; the mismatch still sits in the caches but is no longer a manuscript defect. *Housekeeping:* the filename `..._qpu_vs_classical.pdf` and the now-unused `cache_sparsity_ablation_qpu.json` are stale leftovers.
- **(c) spliced classical curve → VERIFIED FIXED.** *(confirmed)* The dense 288-parameter point is gone; `cache_sparsity_ablation_exact.json` now carries five keys including the native mask, so all four series share the same left edge, and the caption explains the native-hardware-floor line.
- **(d) floor numbers contradicted the figure → FIXED at L544, but a NEW contradiction appeared at L563.** *(confirmed)* L544's rewritten numbers reproduce the committed caches **to the digit** (floor 1.05/1.48/3.45/2.41 % per spin; Metropolis 13.37 → 28.47 %; ratios 7.9–16.9× → "8 to 17 times"). But the new concluding paragraph 19 lines later asserts the error "sits **7–27×** above this floor" — a range no mean or median aggregation of those caches produces (true span 6.6–17.7×). Two incompatible ratios for the same figure. See **N1**.

---

### 2.2 Major findings — 15 of 17 verified fixed

**Verified fixed** *(all confirmed against current text, `build/report.aux`, `report.log`, `report.blg` or the rendered figures)*: **M1** (Eq. 13 now `E = a·v − b·h − h·W·v`, both CEM equations sign-consistent) · **M3/M4** (Eq. 27 now states only the antiperiodic sum, with `J>0`, `h≥0`, periodic BC in prose; the inert `min()` is gone — I re-verified the closed form against dense ED for N ∈ {4,6,8,10}, h ∈ {0.5,1,1.5}: agreement 9×10⁻¹⁶…4×10⁻¹⁴) · **M5** (Eq. 8's stray `=` and unrestricted sum) · **M6** (variational bound restated correctly) · **M7** (`Σ` for the unregularised covariance; main text, Algorithm box, CG section and Appendix now agree) · **M8** ("no intra-layer connections") · **M9** (⟨s⟩ now stated as evaluated on the exact ED ground state; citation moved to `Troyer_2005`) · **M10** (all three cross-references; 26/26 `\autoref` targets resolve, zero `??`) · **M11** ("Classical solvers dominate") · **M12** (prose now in the per-spin units the figure plots) · **M13** (both dotted/dashed elements named) · **M14** (Fig. 15b now shows all 3 seeds with × for divergence; the prose flags the small sample) · **M15** (β_x sweep extended to 0.90; the h=0.5 optimum is now a genuine interior minimum) · **M16** ("quantum-assisted Variational Monte Carlo", with VQE kept as one contrastive reference) · **M17** (Pauli convention and `v,h ∈ {−1,+1}` now stated; Marshall transformation Pauli-consistent) · **M18** (both headings wrapped in `\texorpdfstring`; all 46 bookmarks decode cleanly, zero hyperref token warnings).

**M2 — resolved differently than recommended, and the resolution is better.** *(confirmed)* Code inspection established that neither textual description was accurate: the estimator pools over an entire batch of ordinary joint samples with **no clamping of `v`**, fitting one β by least squares. The manuscript now describes that, and Eq. (19) is a double sum over samples and hidden units. Consequence for this audit: `verify/cem_objective.py`'s 24.8 %-saturation figure describes a single-condition estimator that the code never implemented, so it should be read only as a general note that single-condition matching is noisy — not as a measurement of this implementation.

**M19 — fixed, but each fix exposed a latent defect in a newly-published entry.** *(confirmed)* Months, the Richter title bracing, and the `jaxGlossaryTerms` fields are all correct, and `bibtex` now reports zero warnings. But publishing two previously-uncited entries revealed: reference **[5]** prints literal `{M}{P}{I}{P}{K}{S}` braces in its URL, and reference **[15]** prints "**Veloxq: A fast and efficient qubo solver**" — the identical `unsrt` case-folding bug M19 fixed for Richter, reintroduced. Also reference **[6]**, the paper the entire CEM method comes from, prints with no locator or arXiv identifier.

**Still not fixed: 13 of 19 §2.3 minors.** Several are one-line edits: duplicate `\usepackage{graphicx}` (L7, L12) · stray `*` in the appendix divider · italic `$20\,\mu s$` and the document's single overfull box (same paragraph as before) · the `f(x^n)` / `q(x_n|x*)` slips inside Eq. (12) · the spurious "thermodynamic limit" · `σ_y` declared but absent from the equation it follows · SRBM undefined · the Lanczos description · `D_TV` normalisation · LRTFIM Kac normalisation · the coupler-type descriptions · the `\sqrt{}`-ansatz convention statement. Two got worse: **`W_{ij}` vs `W_{ji}`** is now spread across four equations plus the new code listing and disagrees with L675's shape comment; and the "**solid markers**" caption still contradicts its legend (I re-rendered it — the "hidden" swatch is an empty white rectangle).

---

### 2.3 New findings in the material added since `973f11b`

The 136 inserted lines are a clear net gain in substance, but they carry 24 new defects. The serious cluster is in §4.2, the newest subsection.

**N1 — Two incompatible ratios for the same figure, 19 lines apart.** *(confirmed)* L544 says "8 to 17 times larger than the floor"; L563 says "7–27× above this floor". The caches give 6.6–17.7×, matching L544's construction. One of the two is stale. Also `$7$-$27\times$` renders its range separator as a minus sign — use `--`. **Highest-priority fix in the document.**

**N2 — §4.2's prose contradicts its own figure, twice, and both versions are false.** *(confirmed by decoding `tte_vs_n_eps_0p01.pdf`)* L328 says censoring at the tight target begins "first for Gibbs, then for Metropolis, LSB +CEM, and the QPU results, while FPGA and VeloxQ continue to reach ε = 0.01 throughout the tested range", then that "by N = 128 no solver reaches the tight target". Pixel-level reading of the panel shows: **FPGA and VeloxQ are themselves censored (0/20) at N = 128** and annotated 12/20 and 19/20 as early as N = 24–32; **LSB is drawn solid with 4/20 at N = 128**; and the earliest censoring anywhere is **Zephyr QPU at N = 16 (5/20)**, not Gibbs. Rewrite the paragraph from the figure.

**N3 — Figure 7 cannot be decoded from its caption.** *(confirmed)* The caption (L346) says hollow markers mark sizes where **at least one** seed was censored. In the rendered figure, FPGA at N=32 ("12/20") and VeloxQ at N=24 ("19/20") are **filled** despite 8 and 1 censored seeds. Hollow appears to mean 0/20. Either the caption or the plotting script is wrong; until it is settled no reader can interpret the report's headline timing comparison.

**N4 — The headline speed claim rests on an undisclosed configuration.** *(confirmed)* The figure legend reads "VeloxQ **(SA, untuned)**"; the word "untuned" appears nowhere in the body, the caption, or the hardware-configuration subsection, which instead gives a fully specified FPGA/VeloxQ configuration (L706). Either disclose it in the prose or drop it from the plot.

**N5 — "fastest by roughly two orders of magnitude" is unqualified and false at the largest size.** *(confirmed)* In the loose-target panel VeloxQ climbs to ≈7 s at N=128, above Gibbs (≈1 s) and LSB (≈5 s). Add "at small N".

**N6 — The section title collides with a metric the report formally defines.** *(confirmed)* §4.2 is titled "Time-to-solution across solvers" but measures **TTE** (time-to-ε); **TTS** is defined by Eq. (1) 267 lines earlier as a different quantity. The PDF running head says one thing while the first sentence of the body says the other. Rename to "Time-to-ε across solvers".

**N7 — `\epsilon` / `\varepsilon` collision.** *(confirmed)* The new section makes `\epsilon` an accuracy target **on** energy error per spin, while `\varepsilon` already denotes energy error per spin (L302, L499, L544, L560) and `\epsilon` already denotes the TFIM quasiparticle dispersion (L656–658). Three meanings across two nearly identical glyphs.

**N8 — "following the convention used elsewhere in this work" describes a convention that does not exist.** *(confirmed)* Figure 14 marks divergences as "a/b" annotations, Figure 15b uses `×` markers, and only Figure 7 uses hollow-for-censored — three marks for two different concepts.

**N9 — Two different β_eff estimators share one symbol with no comment.** *(confirmed)* §4.3.1 estimates β_eff by **TV-argmin** (L376), §4.3.2 and §4.3.3's ground truth by **KL-argmin** (L398, L432). Since §4.3.2's whole point is a quantitative comparison against §4.3.1's LSB behaviour, the switch must be stated.

**N10 — §4.3.3's index `i` means two different things within six lines.** *(confirmed)* Visible-unit index at L423, sample index at L425–429, and L429 silently renames the visible index to `l`. Use `s` for samples, matching L625 and L723.

**N11 — Bias figures quoted on two incompatible aggregations, presented as one.** *(confirmed)* L432 gives "−0.07 to −0.08" and then "≈−0.19 at β_x=0.5" — the first averaged over β_x, the second conditioned on it, with nothing saying so. Also use "largest in magnitude" for a negative quantity.

**N12 — Unsupported comparative claim.** *(confirmed)* L429 says the pooled estimator "is also lower-variance **in practice**", but the validation measures bias and RMSE against an exact estimator and never runs a head-to-head against single-condition CEM. Downgrade to an expectation or add the comparison.

**N13 — The Methods CEM paragraph now duplicates §4.3.3 in clashing notation.** *(confirmed)* Two derivations of the same original formulation from the same citation, ~200 lines apart, with `c_j` vs `b_j`, `\operatorname*{arg\,min}_{\beta>0}` vs `\arg\min_\beta`, SRBM framing vs Boltzmann-machine framing. Cut L212–221 to the pointer L211 already provides.

**N14 — Smaller items in the new text.** *(confirmed)* "overtaking … to become the slowest" inverts the verb (L328) · body says the Zephyr chip is the size constraint while the caption and legend show both Pegasus and Zephyr (L326 vs L346) · "SAPI" used once, never expanded, and bare `h`/`J` reused for qubit bias and coupler strength after 300 lines in which `h` is the transverse field (L388) · the code listing consumes `energies` without producing it (L393–399) · `LSB~+CEM` renders as "LSB +CEM" while the legend says "LSB (+CEM)" · reviewer-response register in the manuscript ("the head-to-head timing comparison … previously missing from this work", L328; the same register leaks into `scripts/dtv_autoscale.py`'s docstring) · L542 points at Figure 14 as a whole for a claim only panel (b) supports · "For budget constraints" and "representability" (L563) · Figure 11's caption is the only one without a terminal period, and "β_eff = 1.94 hugs the data" attributes to a value what the curve does · markup drift: `\emph` only at L388 against 19 `\textit`, `\subsubsection{CEM}` the only bare-acronym heading, the four new CEM subfigures the only ones missing `\centering`, `\subcaption` vs `\caption` mixed inside subfigures · `D_TV` now appears in **four** spellings (`D_{TV}` typesets as an italic product), `β_eff` in two · four `~\cite` sites against six that butt directly against the preceding word · 21 lines with trailing whitespace and a three-blank-line run at L606–608.

---

## 3. Completeness — updated

### 3.1 Closed or substantially advanced

- **QPU β_eff is now measured** (§4.3.2) — was a major gap.
- **A QPU `D_TV` now exists** (L406, Figure 9a) — was critical gap 1. *Partially:* it is a by-product of the auto-scale sweep, plotted against β_x rather than sampling effort, so it is not comparable with Figure 6, and the Sampling Quality section (L285–323) is still SA/Metropolis/Gibbs/LSB only and never mentions the QPU.
- **A cross-solver wall-clock comparison now exists** (§4.2) — was critical gap 2. Seven series (FPGA, VeloxQ, Metropolis, Gibbs, LSB, LSB+CEM, QPU) at matched hyperparameters, median over up to 20 seeds with IQR, censored runs retained. *Caveats:* the timing basis is not stated (QPU access time versus total wall clock including programming, readout and network latency — decisive for a QPU-vs-classical claim); the N=128 points are described as "extrapolated" with no method; and N2–N5 must be fixed before the comparison is usable.
- **Sizes now exceed the enumerable range**: N up to **128** classically, QPU to 64 — was "largest N = 16". Critical gap 3 is softened, though the models remain exactly solvable, so "computationally hard problems" is still not literally delivered.

### 3.2 Still open

1. **No abstract, no Discussion, no Conclusions** — `grep` returns zero for all three in both the source and the compiled PDF. The question posed at L52 is still never answered, and the document ends on the appendix derivation.
2. **No data/code availability statement** — zero hits for `availab|repositor|github|zenodo`, although the caches are committed and the manuscript now names specific scripts (`scripts/dtv_autoscale.py`).
3. **`\date` still unset**, so the title page stamps the build date — currently "August 7, 2026", and it changes on every recompile.
4. **LRTFIM and XXZ still appear in zero results** (L97–102, L113–121), and L662 still justifies exact diagonalisation by invoking long-range interactions that never appear.
5. **The sparse-embedding section still does not test its own hypothesis**: no dense-with-chains versus chain-free comparison at equal N, and no qubit-count or QPU-time saving quantified.
6. **CEM is still never applied to the QPU**, though L221 asserts it can be — and §4.3.2 now makes this the obvious next experiment, since it derives the calibration (β_x ≈ 4.1) that would be needed.
7. **No headline accuracy number for QPU-driven training** at any N.
8. **Parallel-embedding controls** still absent: no statement whether `num_reads` was divided by `n_parallel`, no chain-length or chain-break statistics, no independence check.
9. **Missing hyperparameters**: numeric η, λ, CG tolerance, LSB timestep/pumping/noise; the "sampling floor" is still defined only inside captions. There is **no table environment anywhere** in the document.
10. **The framing contradiction** (which hard-but-stoquastic class remains the target) is unaddressed; `grep stoquastic` → 0.

---

## 4. Novelty and positioning — unchanged, with one addition

Revision 3's assessment stands: the CEM validation is pre-empted by Kubo & Goto (arXiv:2512.02323), the sparse chain-free RBM is incremental against Park et al. (UCNC), Golubeva & Melko (PRB 105, 125124), Pilati & Pieri (PRE 101, 063308) and Marshall et al. (PRR 2, 023020), and parallel embeddings are standard practice (Pelofske, Hahn & Djidjev, Sci. Rep. 12, 4499). The sampling-quality benchmark sits in the territory of **Berns, Rodrigues, Finocchio & Mentink, Phys. Rev. Applied 25, 024085 (2026)** (arXiv:2504.18359), and the residual open gap — an SB-class sampler with per-iteration effective-temperature correction inside an NQS/VMC loop — is narrow and inside one group's active programme (Mentink co-authors both Berns and Chowdhury et al., arXiv:2512.24558). The defensible differentiator remains the **mechanism**, not the hardware class. §4.3 of revision 3 lists the still-missing citations; none has been added.

**One addition.** The auto-scale result is a genuine, citable calibration contribution and the report currently undersells it as a caveat. "On D-Wave with `auto_scale` enabled, a uniform β_x rescaling of an RBM cannot control the sampling temperature; β_eff is pinned at ≈2.8, and disabling `auto_scale` restores β_eff ≈ 4.1/β_x" is precisely the kind of practical, negative, hardware-specific result Phys. Rev. Applied publishes — and it is directly useful to everyone in the quantum-assisted-Boltzmann-machine line, who mostly leave `auto_scale` at its default. Claim it in the abstract that does not yet exist.

---

## 5. Readability — much improved, with one blocking defect

**Genuinely fixed.** Every one of the 15 named language errors is gone, and a dictionary pass over the de-TeX'd prose of all 772 lines finds **zero misspellings**, new material included. Cross-reference health is now clean: 33 `\autoref`s, 33 resolving targets, no duplicates, no `??`. All 46 PDF bookmarks decode cleanly with zero hyperref token warnings. `bibtex` reports zero warnings. All 33 `\includegraphics` targets exist on disk, including every figure of the new sections.

**Blocking.** Figure 7 is undecodable (N3) and the paragraph introducing it is factually wrong about it (N2). That is the report's headline timing comparison.

**Structural, unchanged.** No abstract, no conclusions; §5 "Implementation" (methods) still follows §4 "Experimental Analysis" (results); §3 and §4.4 each have exactly one child subsection; the JAX tutorial and the Appendix still read as thesis material.

---

## 6. Reproducibility

**Improved.** The sparsity floor's cache (`cache_sparsity_ablation_exact.json`) and both of Figure 14's plotting scripts are now committed, so all four series in panel (b) are reproducible — revision 3's finding that one curve had no data on disk is closed.

**Open, and one item is new.**

- **F1's headline numbers are not reproducible.** Neither repository contains a `cem_validation` cache or its generating script; `verify/cem_validation_fixed.py` itself notes the real checkpoints are unavailable here. The most important corrected number in the paper currently rests on a run nobody else can repeat.
- **The implementation repository on this machine predates every fix.** `/Users/bartek/Desktop/adiabatic-boltzmann` is at HEAD `2383dacf` (2026-06-16), 69 commits behind its remote; none of `scripts/exper/cem_validation_sweep.py`, `scripts/viz/plot_cem_validation.py`, `scripts/dtv/dtv_beta_scale.py`, `plot_sparsity_ablation_floor.py`, `exact_ansatz_floor.py` or `cem_matching_demo.py` exists there. **Every code-side claim in this audit's history is therefore `cannot verify here`** — the fixes may well be exactly as described, but a reader with this checkout cannot confirm them. Pull the remote before the next review pass.
- **The seeding sentence still contradicts the caches**: L708 describes seeding "via `np.random.randint` feeding `jax.random.PRNGKey`", while every cache key ends in one of five fixed seeds `{42, 123, 456, 789, 1234}` that appear nowhere in the manuscript.
- **Cache semantics remain trap-laden and undocumented**: iteration count is `len(energy_history)`, not a field; the seed lives only in the key; key field 2 means target sparsity in the ablation caches but α in `cache_full.json`; `E_final` is a fresh re-evaluation differing from `energy_history[-1]` by up to 6 % of `|E_exact|`.
- Sample budgets and seed counts are still absent for several figures, and there is still no data/code availability statement.

---

## 7. What to do next

*(Findings above are verifiable. The ordering below is judgement.)*

### P0 — the report is currently unreadable at its headline claim (hours)
1. **N1**: reconcile 8–17× (L544) with 7–27× (L563); the caches support L544.
2. **N2/N3**: rewrite L328 from the figure, and settle the Figure 7 marker convention in whichever of caption or script is wrong. Until this is done the timing comparison cannot be read.
3. **N4/N5/N6**: disclose or drop "(SA, untuned)"; qualify "two orders of magnitude" with "at small N"; rename §4.2 to "Time-to-ε across solvers".
4. **F2 residuals 2 and 3**: qualify L260 in place, and replace "offset set by the chip's own physical temperature" with "a constant prefactor ≈4.1, set by the chip's operating temperature together with the programmed energy scale, freeze-out and control error".
5. Fix the two bibliography exposures (reference [5]'s braces, [15]'s case folding) and give reference [6] a locator; sweep the 13 remaining §2.2 minors, most of them single-character edits.

### P1 — before any submission (weeks)
6. **Propagate F2** (residual 1): add the β_eff ≈ 2.8 caveat wherever QPU samples are used, or re-run at `auto_scale=False` with β_x ≈ 4.1 — which would also close item 6 of §3.2 (CEM on the QPU) and give the report its first temperature-correct QPU results.
7. State the **timing basis** of §4.2 explicitly (what is inside the QPU's measured time), and the extrapolation method behind the N=128 points.
8. Add: an **abstract** (claiming the auto-scale result), a **Discussion/Conclusions** section answering L52, a **data/code availability statement** naming the caches, solver IDs and the five seeds, a pinned `\date`, and an **experimental-protocol table** (one row per figure: model, N, sampler, budget, seeds, statistic, baseline).
9. Commit the CEM-validation cache and script so F1's corrected numbers are reproducible; pull the implementation repository so the code-side fixes are checkable.
10. Either add LRTFIM/XXZ results or cut those Methods subsections; add the missing citations of revision 3's §4.3; reframe the sparse and parallel-embedding work as method notes with their prior art, and claim the auto-scale calibration as a contribution.
