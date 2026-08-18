# Audit: *Quantum Variational Algorithms on Adiabatic Quantum Computing Devices* (`report.tex`)

**Revision 10** — 2026-08-18. Revision 9 corrected after a second review round. That round is right on five of its eight points, one of which forced a rewrite of B2 and the withdrawal of a sub-finding of B1; it is wrong on the one point it calls a new blocker, and the refutation is given in §3.9. History and the list of corrections in [`CHANGELOG_audytu.md`](CHANGELOG_audytu.md).

**Pinned targets.** Manuscript: the 777-line working tree, i.e. `6793638` plus the merge `482c7cb` of `0d846c2` ("final changes"). Implementation: `iitis/adiabatic-boltzmann` at **`a4b0f2006`** ("integrated all result files together, energy corrected"), fetched and inspected for this revision. Both must be pinned in any future audit — the implementation repository moved from `4746ef128` to `a4b0f2006` while revision 8 was being written, which is exactly how revision 8 got its reproducibility section wrong.

**Method.** All file access via `sed`/`grep`/`awk`/`python3`/`pdftotext`/`pdftoppm`. Claims were re-derived rather than read: the TFIM closed form against dense exact diagonalisation over 90 (N, J, h, boundary-condition) cells; the RBM trace-out and the CEM conditional against brute-force enumeration; the average sign against exact diagonalisation of the J₁–J₂ chain; the CV stopping rule against tuned trial states; every sparsity number recomputed from the committed caches; figure values extracted from vector paths and 150–320 dpi renders; DOIs checked against Crossref; the implementation repository inspected at the pinned commit.

**Confidence.** `confirmed` = verified against a file, build artefact, committed cache, decoded figure or external source. `measured` = extracted from a rendered figure. `derived` = computed here. `inference` = follows from verified facts but has an untested step.

---

## 0. Before anything else — not a manuscript issue

**A private bank document is in this repository's history, and the remote is public.** `figures/2_5316856890368498963.pdf` — tracked since commit `92acd8d` (message: `]`), never referenced by any `\includegraphics`. `pdfinfo` gives Author "ING Bank Śląski S.A."; the text is a transaction confirmation whose payer block contains a full name and home address, plus payee details and an account number. `git remote -v` → `https://github.com/atg205/adiabatic-boltzmann-report`. *(confirmed)*

The file is now untracked and `.gitignore`d (commit `efa3156`) and still on disk — that only stops it being re-added. **It remains in the history**, so treat it as public since `92acd8d`:

```
git filter-repo --path figures/2_5316856890368498963.pdf --invert-paths
git push --force-with-lease --all
```

then ask GitHub Support to expire the cached object. Before running it: take a full backup clone, expect `git filter-repo` to drop the `origin` remote as a safeguard (re-add it afterwards), and make sure every ref and tag is rewritten, not just `main`. This rewrites shared history, so it is your decision — but it is the one step left.

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

1. **B1 — The headline scaling claim is confounded by a size-dependent stopping rule** (§3.1). This is the paper's contribution sentence.
2. **B2 — The axis is labelled wall-clock training time but plots sampler time**, the two sampler clocks have different boundaries, and the median is conditioned on success in cells where it is unidentified (§3.2).
3. **B3 — The solver-ordering sentence (L542) is false against its own figure**, for the second consecutive revision (§3.3).
4. **B4 — The abstract and Conclusion overclaim**: a strict FPGA win "at every size tested" that the body contradicts, and an energy claim covering "classical and quantum alike" when QPU energy was never measured (§3.4).
5. **B5 — "We tested the sparse models only on classical hardware" is refuted by 20 committed QPU runs** — which are not budget-matched, so the fix is disclosure, not restoration (§3.5).
6. **B6 — The sign-problem instrument is identically zero** for every model it is introduced for, and the figure that would supply its missing evidence is already committed and never included (§3.6).
7. **B7 — Two citations do not support their claims** (§3.7).
8. **B8 — The threshold sensitivity is undisclosed, and the shipped figure cannot be produced by any committed code** (§3.8). This compounds B1.

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

### 3.1 B1 — The headline scaling claim is confounded by a size-dependent stopping rule *(the size dependence is `derived`; the causal attribution is `inference`)*

The abstract and Conclusion argue the annealer "scales more favorably … pointing to quantum competitiveness at larger scale", sourced from the legend's fitted exponents: **Pegasus ∝ N^−0.38, Pegasus+CEM ∝ N^−0.35, Zephyr ∝ N^+0.06, Zephyr+CEM ∝ N^−0.55** against **FPGA ∝ N^1.90**. *(measured)*

A negative time-to-ε exponent says the annealer converges *faster* on bigger problems. The gate is CV = std(E_loc)/|mean(E_loc)| < 0.05, and CV falls as N^(−1/2) at fixed energy error per spin: measured on TFIM trial states tuned to exactly 0.1 error/spin against H(h=0.5), **CV = 0.1613 / 0.1408 / 0.1265 at N = 8/10/12 while CV·√N = 0.456 / 0.445 / 0.438 — constant to 4 %**. So the gate loosens with N, and the solver whose per-iteration cost grows slowest benefits most. *(derived)* Extrapolating that scaling to N=64 gives a factor ≈2.8, but that step assumes the N^(−1/2) law holds beyond the sizes measured here and at the accuracy the QPU runs actually reach — treat the factor as indicative, not exact.

**What this does and does not establish.** It establishes that the gate is not equally hard at every N, so the fitted exponents are confounded with the criterion. It does **not** by itself prove the negative exponents are pure artefact — that requires the decisive test, which has not been run: recompute the *actual* QPU and FPGA histories (they are committed upstream, `history` field) under a size-independent criterion, either CV·√N < const or a direct oracle-based energy-error crossing, and see whether the ordering and the exponents survive.

**Fix:** run that recomputation and report it; or remove the scaling claim from the abstract and Conclusion and state what was measured. Until then the claim is not supported, whether or not it turns out to be true.

### 3.2 B2 — The axis is not what it is called, and the two sampler clocks have different boundaries *(confirmed in the pinned code)*

Revision 9 said the classical series carry the full host-side SR cost that the QPU series have zeroed out. **That was wrong**, and the pinned implementation settles it: the timer starts immediately before `sampler.sample(...)` and stops immediately after, and the energy meter is active only around that same call. The code says so explicitly — "Only the `sampler.sample()`/`sample_parallel()` calls are metered … SR/CG/gradient work also runs on the GPU but isn't solver cost, so it's excluded." Both sides exclude the SR solve, the local energies and the gradients.

What survives is sharper. **First, the axis is mislabelled.** L539 defines TTE as "the wall-clock time until training reaches a validated convergence" and the caption repeats it, but what is plotted is **sampler time to validated convergence** — for every series. A reader comparing solvers on "time to train" is reading a quantity that excludes most of training. The same applies to the energy panel: it reports GPU energy drawn during sampling, while the abstract says "energy consumed to reach it".

**Second, the two sampler clocks still have different system boundaries.** The QPU number is the device-reported `qpu_access_time` (on-chip programming, anneal, readout), excluding queue and network; the classical number is host wall-clock around the sampler call, which includes host-side dispatch and transfer. These are not the same kind of measurement, and the caption's "absolute scale stays directly comparable" asserts that they are.

**Third, the plotted median is conditioned on success.** Four cells have fewer than 10/20 events, where a median under censoring is formally unidentified — Pegasus 2/20 at N=8, Zephyr 5/20 at N=16 and 6/20 at N=32, FPGA 6/20 at N=64, three of them in the classical-versus-quantum panel. The 2/20 and 5/20 cells are drawn with **zero-length IQR bars** while the 19/20 cell carries a bar spanning a factor of 3.6, so the least-supported cells render as the most precise. *(measured)*

**Fix:** relabel the axis and the caption as sampler time (and the energy panel as sampling energy), or measure end-to-end; state the two clocks' boundaries side by side and drop "directly comparable"; use Kaplan–Meier medians with intervals, grey out cells below ~10/20, and draw no whisker where the quartiles are degenerate.

### 3.3 B3 — The solver ordering is false against the figure *(measured, four independent extractions)*

L542: "panel (b)'s FPGA is consistently fastest, followed by \gls{sa}, then panel (c)'s two QPUs, with panel (a)'s Metropolis and Gibbs and panel (b)'s \gls{lsb} the slowest … both QPUs overtake them at that size."

SA is **slower than every QPU series from N=16 upward** and the **slowest of all nine series at N≥24**, reaching ≈12–13.5 s at N=64; Gibbs, named among the slowest, is flat at 0.7–1.3 s. The legend corroborates: SA ∝ N^1.19, Gibbs ∝ N^0.08. The second clause fails too: at N=64 FPGA (≈0.27 s) sits *inside* the QPU band (≈0.20–0.51 s) — one series faster, one tied, two slower.

**Fix:** generate this sentence and the caption mechanically from `paper_figures.py`'s data structures. This is the second consecutive revision in which a hand-written ordering sentence contradicted this figure.

### 3.4 B4 — The abstract and Conclusion overclaim *(confirmed)*

"Across both metrics, the FPGA-based solver outperforms all other samplers, classical and quantum alike, at the system sizes tested" (abstract) and "the fastest and most energy-efficient sampler at every size tested" (Conclusion) are contradicted by the body at L542 and by the measurement in B3.

On energy the problem is not an asymmetric measurement — L544 states plainly that the QPUs are omitted "because no API exposes per-job energy draw" — it is that **the abstract claims superiority over quantum samplers on a metric for which no quantum number exists**. The FPGA's own energy figure is additionally "an assumed constant power draw of 45 W … since it was never GPU-metered", by the caption's own admission.

**Fix:** restrict the energy claim to the metered classical solvers, mark the FPGA number as an estimate, and state the N=64 crossover honestly.

### 3.5 B5 — An unreported QPU arm that the repository commits *(derived from the caches)*

L474: "Due to budget constraints, we tested the sparse models only on classical hardware." `figures/sparsity/cache_sparsity_ablation_qpu.json` contains **20 records — 4 masks × 5 seeds (42/123/456/789/1234), N=16, Zephyr, each with a populated `qpu_time_ms_used`**. The plotted file is still named `sparsity_ablation_qpu_vs_classical.pdf` while its legend lists only three classical samplers and the exact floor; `sparsity_heatmap_REAL_QPU_zephyr.pdf` is also committed and unused. The withheld arm gives 10.68 / 12.27 / 45.69 / 76.42 % per-spin error.

Restoring it is not clean: the QPU arm ran **14–300 SR iterations** per run (per mask `[26,31,176,205,300]`, `[185,297,300,300,300]`, `[15,28,133,300,300]`, `[14,18,25,32,44]`) against a uniform **300** for every classical run.

**Fix:** state what was actually run — "a real-QPU arm was run but is not reported because its iteration budget was not matched to the classical arms" — or plot it with the mismatch disclosed. A committed dataset that refutes the text is the largest single credibility risk here.

### 3.6 B6 — The sign-problem instrument measures nothing *(derived)*

⟨s⟩ = Σ_v Ψ₀(v) / Σ_v |Ψ₀(v)| is **identically zero** for every model it is introduced for: Σ_v Ψ₀(v) = 2^{N/2}⟨+|^{⊗N}|Ψ₀⟩ vanishes by SU(2) symmetry for any singlet ground state. Measured across 12 (N, J₂/J₁) cells at N = 6, 8, 10 and J₂/J₁ = 0, 0.3, 0.5, 0.7: **|⟨s⟩| ≤ 3×10⁻¹⁶ everywhere**, including the provably sign-free J₂ = 0 case. No number derived from it appears in the paper. In the **Marshall gauge** the same formula is informative: 1.000 → 0.997 → 0.941 → 0.000 at N=8 across J₂/J₁ = 0 → 0.3 → 0.5 → 0.7.

L511's claim that "without the correction the variational energy degrades significantly" also has no evidence in the paper: the cited figure shows one Marshall-corrected curve per panel, no ablation, no mention of the gauge.

**Fix — nearly free:** `figures/marshall_comparison.pdf` is **already committed and never included**, and contains exactly "With Marshall (Ψ = s·A)" / "Without Marshall (Ψ = A)" / "Average sign ⟨s⟩" against J₂/J₁. Include it, state the gauge, and either evaluate ⟨s⟩ in the Marshall gauge or delete the definition.

### 3.7 B7 — Two citations do not support their claims

- **L109** cites `mpg` as the sole authority for the Heisenberg model. The cited PDF is 5 pages, its only heading is "Transverse-field Ising model", and full-text search returns **zero** hits for "heisenberg", "exchange", "isotropic" or "XXZ" — so the source does not support the claim. Its PDF metadata are empty, so the bibliography record's title, author and year cannot be traced to it; that is a provenance problem, not proof of fabrication. *(confirmed for the content; `inference` for the record's origin — please check the record's source yourself.)* **Fix:** cite Heisenberg (1928) or a textbook; the lecture note is a correct source for the TFIM subsection, which has no citation at all.
- **L560** credits Stochastic Reconfiguration to `Sorella_2001`, whose own abstract says SR "has been recently introduced" — i.e. elsewhere (Sorella, PRL 80, 4558 (1998)). *(confirmed)* **Fix:** cite the 1998 PRL for the method, 2001 for the variant.

### 3.8 B8 — Undisclosed threshold sensitivity, and a figure the pinned code cannot produce *(confirmed at `a4b0f2006`)*

The paper presents CV < 0.05 and ε = 0.1 per spin as *the* protocol. Upstream the generator's signature is `fig10c_tte_vs_n_self_convergence(cv_threshold=0.05, window=10, epsilon=0.01)` — ε defaults to **0.01**, ten times tighter — and the repository holds **five** fig10c variants over cv ∈ {0.03, 0.05} × ε ∈ {0.01, 0.1} plus two fig10d variants. The manuscript reports one cell of that grid, the loosest on ε, and never mentions the others.

The existence of those files does **not** show the pair was chosen after seeing the results — they are equally consistent with a robustness sweep or with figure development, and revision 9 overstated this. What it does show is that a sensitivity analysis exists and is undisclosed, which matters because the fitted exponents, the censoring pattern and therefore B1's claim are all functions of (CV, ε).

**The provenance problem is larger than the missing suffix, and this part is decisive.** The figure shipped in the paper is not the upstream artefact:

| | report `fig10c_tte_vs_n_self_convergence.pdf` | upstream `…_cv0.05_eps0.1.pdf` |
|---|---|---|
| SHA-256 | `4a56be72…` | `ded0bc94…` |
| fitted `∝ N^p` labels in the plot text | **9** | **0** |

The pinned `fig10c` function contains no exponent fitting at all (`polyfit`/`curve_fit`/slope → zero hits), and its `__main__` block calls eleven figure functions but **neither fig10c nor fig10d**. So the exact artefact on which the paper's headline scaling claim rests — the one carrying the exponents — cannot be produced by any committed state I can see.

**Fix:** report a sensitivity table over all four (CV, ε) pairs — validated counts, medians, exponents — and say which pair the paper reports and why; and commit the code that actually generated the shipped figure, with the parameterised filename restored so the artefact is traceable to its generating call.

### 3.9 Examined and rejected: the "forward-looking plateau window"

A review round raised, as a new blocker, that `compute_validated_convergence_iter` validates the wrong iterations — that `plateau = energies[conv_iter-1 : conv_iter-1+window]` takes the detection point plus up to nine *future* iterations instead of the window that triggered the detector, which would put every `n/20` count, median and exponent in doubt.

**It does not.** `compute_convergence_iter` returns `conv_iter = t − window + 2` when the run of `window` passing iterations ends at 0-indexed `t`, i.e. `conv_iter` is the **1-indexed first iteration of the plateau**, not the detection point. Then `conv_iter − 1 = t − window + 1` is that same iteration 0-indexed, and the slice spans `t−window+1 … t` — **exactly the triggering window**. Verified for detection at t = 9, 15 and 42: slice and triggering window coincide in every case. *(derived)*

This also **withdraws a sub-finding of revision 9's B1**: that the QPU medians correspond to 4–9 iterations, "fewer than the 10 the rule requires". Since `conv_iter` marks the plateau's start, a TTE below ten iterations is expected behaviour, not an inconsistency.

One legitimate residual remains, worth a sentence in the paper rather than a finding: because TTE is reported at the plateau's **start**, it excludes the ten iterations of confirmation the rule needs before it fires. That flatters every series equally, so it does not affect the ordering, but the reported time is time-to-plateau-start, not time-to-detection.

---

## 4. Major findings

**M1 — The energy figure's caption contradicts its own annotations.** It claims "the same validated-convergence cells" as the TTE figure, but the TTE figure carries 19 `n/20` annotations and the energy figure 10, overlapping in exactly one value. The same cells under the same censoring rule cannot yield different validated fractions. *(measured)*

**M2 — Figure 4(a)'s caption is wrong by a factor of two.** It says "24 visible and 24 hidden units"; connected-component counting on a 150-dpi render gives **12 and 12**, and panel (b) corroborates with 24 chain qubits, one per logical node. *(measured)*

**M3 — The hardware paragraph contradicts itself about simulated annealing.** L676 says all non-QPU methods including SA run "locally via JAX on a single NVIDIA TITAN RTX GPU", then states SA uses `dwave-neal` — a single-threaded CPU sampler. This is load-bearing twice: SA's wall-clock is a plotted series, and the energy panel reports **measured** `gpu_energy_wh` for SA. *(confirmed)*

**M4 — The benchmark's parameters are stated 130 lines from the figure, and one is still missing.** The protocol (TFIM, h=0.5, seeds 0–19, sampler table) lives in the Implementation section at L678, not in the time-to-ε section or its caption, and the **hidden-unit count is given nowhere**. Also ε=0.1 per spin is a **9.4 % relative** energy error at h=0.5 (|E₀|/N = 1.0635), against the 0.01 % the same model and size reaches in the spin-ordering figure — worth stating in relative terms. *(confirmed / derived)*

**M5 — Coverage.** The figure spans N∈{8,12,16,24,32,64} but the QPU series appear at only four sizes. The text gives the correct explicit set, so this is a coverage limitation to acknowledge rather than a false statement; "should not be mistaken for a QPU coverage gap" is nonetheless a strange way to describe a figure in which the QPU covers four of six sizes. *(measured; softened from revision 8)*

**M6 — The sparsity floor's shape is one outlier seed.** Per-seed values at mask 0.809 are **1.97, 2.02, 2.22, 3.53, 7.49 %**; with medians the floor is 1.06/1.51/2.22/2.44 % — monotone, a 2.3× rise, peaking at the **fourth** mask, so "roughly triples before falling back, peaking at the third mask" is an artefact of a 5-seed mean. The "8–17×" band holds only for Metropolis (7.89–16.88×); across the three samplers it is **6.6–16.9×** (SA = 6.58× at mask 0.809). Gibbs is non-monotone (12.16 → 21.42 → 34.39 → 28.44 %), against the claim that error "increases sharply as sparsity increases". *(derived)*

**M7 — The Fig. 14(b) legend box covers three of the four floor markers the text quotes.** *(measured)*

**M8 — The parallel-embedding numbers are total run lengths, and the claim rests on one seed.** "13.6 s versus 5.7 s" are the right-hand endpoints of the two curve families, not times-to-plateau (the converging n=5 seed plateaus by ≈0.3 s, the n=1 seed by ≈6.0 s). The same paragraph discloses that **2 of 3 seeds at n_parallel=5 diverge**, so the Conclusion's "more effective use of quantum-annealer time" rests on a single seed; 2.4× is also strongly sublinear against the naive 5×. *(measured)*

**M9 — Figure 1's trend and the abstract's point in opposite directions, and the scopes are never separated.** There is no logical contradiction — Figure 1 is a TTS benchmark for rotation/factoring encodings and the abstract's claim is a TTE benchmark for RBM-VMC — but the two are three pages apart with nothing telling the reader they are different problems, metrics and protocols. Its caption says "on current QPU hardware, classical (or even random) approaches asymptotically outperform the quantum annealer", three pages from an abstract claiming the annealer "scales more favorably". Panel (b) also contradicts its own caption (only the MC encoding is asymptotically worse than random; CFA at 2^−0.9l beats it, and the body says so). "Classical solvers dominate for N ≳ 100" understates panel (a), which shows dominance across the whole 16–112 range with no crossing. Per its generator's docstring, panel (a)'s points were **digitised out of the published figure's vector paths** — disclosed nowhere in the manuscript. *(confirmed)*

**M10 — Attribution.** Thirteen sections carry zero citations, including the whole of SB/LSB, the sampling-temperature section, and both embedding contributions, so both read as novel where prior art exists. Absent entirely: **Carleo & Troyer 2017** for the neural-quantum-state ansatz that is the paper's core method (`grep -i carleo` returns nothing anywhere); King et al. 2025 for the beyond-classical claim the paper is framed around; Goto et al. 2019 for SB; Metropolis/Hastings, Kirkpatrick and Geman & Geman (Metropolis–Hastings is cited only to a blog post with an empty year); Marshall 1955; Benedetti et al. 2016; Pelofske et al. 2022. Richter 1994 is a square-lattice result used for a 1D chain, and the average sign is attributed to Troyer & Wiese, who define a ratio of partition functions rather than of amplitudes. *(confirmed)*

**M11 — Four bibliography records are factually wrong.** `veloxq` lists an author replaced in v2 of that preprint (updated 2026-05-04) while linking to a version-less URL now serving v2 — on a collaborator's paper. `willsch2024state` is cited as a 2024 preprint but was published (NIC Series 52, 239–250, 2025, DOI `10.34734/FZJ-2025-01965`). `Mehta_2025` prints "112(3)" with no locator; the article number is 032616. `rrf3-jm5m` uses `issue`, which `unsrt` ignores. Two `@misc` entries print undated. `\bibliography` precedes `\bibliographystyle`. *(confirmed)*

**M12 — Reproducibility: the artefacts exist; the pointers to them do not.** At `a4b0f2006` the implementation repository contains the figure generator, the paper's own validated-convergence function, 11 842 result files and the auto-scale data. What is missing is the ability to *find* the right state: the availability statement names the repository with **no commit hash or DOI** — and that repository is a moving target (13 commits between the two states this audit pinned, 82 since the local checkout it was first judged from); `requirements.txt` pins **no versions**; and the QPU runs carry no access dates or solver version strings, although `Advantage_system6` is a family with several calibrations. Separately, `scripts/dtv_autoscale.py` was deleted from the report repository in `2e0c162` (the data survive upstream). Worse, the exact figure the paper ships cannot be regenerated from the pinned state at all (see B8). **Fix:** pin a commit hash or mint a Zenodo DOI, commit the code that produced the shipped figures, pin versions, and record QPU access dates. *(confirmed at the pinned commit — this supersedes revision 8, which judged from a stale checkout and was wrong.)*

**M13 — The seeding sentence contradicts the paper's own seed list.** L676 describes seeding "via `np.random.randint` feeding `jax.random.PRNGKey`", while L678 states seeds 0–19 and the sparsity caches use a fixed {42, 123, 456, 789, 1234}. Unseeded, `np.random.randint` draws from global entropy; it is deterministic only if a global seed was set beforehand, which the paper does not say. **Fix:** describe the actual mechanism, or delete the sentence now that the seed lists are stated. *(confirmed for the inconsistency; `inference` for the non-reproducibility.)*

**M14 — Three defects visible in the rendered PDF.** `hyperref` loaded bare draws coloured rectangles around all 91 link annotations; `listings` with no `\lstset` sets all three code blocks in the roman body font with fixed columns, printing as `@ f u n c t o o l s . p a r t i a l ( …)`; and **two `\label`s sit on one float**, so four cross-references render as "Figure 7 and Figure 7". *(confirmed)*

**M15 — The promised sampling-quality comparison is still absent.** The Sampling Quality section contains no QPU series and no QPU `D_TV` number appears anywhere in the prose; the only QPU distribution-quality data is the auto-scale ablation, run at different sample counts and floors. CEM is deployed on QPU samples but never validated on them, and no β_eff is reported for any QPU run that uses it. The CEM→β_x feedback loop and the RBM→Ising map are never written down. *(confirmed)*

**M16 — The `auto_scale` causal claim is a temperature confound.** L349's "enabling autoscaling dramatically worsens sampling performance" reads as a property of the switch. At the leftmost β_x both settings sit at β_eff ≈ 2.7 with D_TV ≈ 62.5 % and ≈ 63.5 % — the curves coincide where the temperatures coincide; `auto_scale=False` only reaches its minimum ≈29.5 % at β_x ≈ 5.5, where β_eff crosses 1. `auto_scale` does not degrade the anneal; it removes the ability to tune β_eff toward the VMC target. *(measured)*

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
1. Purge the bank PDF from history and force-push; decide what to do about the tracked internal documents and `verify/` scaffolding (§0).

### P0 — methodological, before the manuscript is shown
2. Recompute the committed histories under a size-independent criterion, or withdraw the scaling claim (B1) — it is the contribution sentence.
3. Relabel the time and energy axes as sampler-side quantities (or measure end-to-end), state the two clocks' boundaries, and replace the validated-seeds median with a censoring-aware estimator (B2).
4. Regenerate the ordering sentence and caption from the plotting data (B3); reconcile the abstract and Conclusion and restrict the energy claim (B4, M1).
5. Say what was actually run on the QPU for the sparse models, and rename the figure file (B5).
6. Include the already-committed Marshall comparison and fix or drop the average sign (B6).
6a. Publish the (CV, ε) sensitivity table, and commit the code that produced the shipped figure with its parameterised filename (B8).

### P0 — attribution and figures
7. Fix the two misattributed citations; add Carleo & Troyer, King et al., Marshall, Goto, Metropolis/Hastings, Kirkpatrick, Geman & Geman, Benedetti, Pelofske (B7, M10).
8. Fix the Fig. 4(a) node count (M2), the SA hardware contradiction (M3), Fig. 1's caption and its undisclosed provenance (M9), and state the hidden-unit count and relative ε at the benchmark (M4).

### P1 — before submission
9. Add a QPU `D_TV` measurement comparable to the classical benchmark; report β_eff for QPU runs using CEM; write the RBM→Ising map and the CEM→β_x loop (M15).
10. Fix the sparsity claims to match the caches — median floor, per-sampler ranges, Gibbs non-monotonicity, legend occlusion (M6, M7).
11. Restate the parallel-embedding numbers and add seeds at n=5, or soften the Conclusion (M8).
12. Pin a commit hash or Zenodo DOI in the availability statement, pin library versions, record QPU access dates (M12); correct the seeding sentence (M13); fix the four bibliography records (M11); reframe the `auto_scale` causal claim (M16).

### P2 — polish
13. `\hypersetup{hidelinks}`, `\lstset`, split the double-labelled float, `\appendix`, pinned `\date`, notation collisions (`M` vs `N_h`, two meanings of α, `N` overloaded in the factoring caption), figure citation order, and an English-language edit (M14).
