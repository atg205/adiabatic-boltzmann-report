# Audit: *Quantum Variational Algorithms on Adiabatic Quantum Computing Devices* (`report.tex`)

**Target:** `report.tex` at commit **`973f11b`** — 712 source lines, 21 compiled pages, 33 numbered equations, 13 figures, 15 bibliography entries (12 cited). Confirm with `wc -l report.tex` (→ 712) and `sed -n '91p'` (→ `H=-J\sum_i\sigma_i^z\sigma_{i+1}^z-h\sum_i\sigma_i^x`). Equation numbers are anchored to `build/report.aux`; line numbers will shift after edits, so re-anchor with `grep -n` before acting on a batch.

**Revision 3** (2026-07-28), incorporating a reviewer critique of revision 2. Revision history, including the errors of revisions 1 and 2, is in [`CHANGELOG_audytu.md`](CHANGELOG_audytu.md).

**Every quantitative claim below is reproducible.** Scripts in [`verify/`](verify/):

| Script | Reproduces |
|---|---|
| `verify/cem_family.py` | Finding **F1** — the bias induced by the CEM validation's reference family (fixed seed 7) |
| `verify/cem_objective.py` | Finding **M2** — consistency and boundary-saturation rate of the Eq. (20) objective (fixed seed 11) |
| `verify/tfim_e0.py` | §2.1 exact-solver verification, the inert `min()`, the parity regimes, and the J<0 odd-N failure |
| `verify/cache_budget_stats.py` | Finding **F3** — every number derived from the committed QPU/classical caches |

**Confidence labels** are attached to each finding: `confirmed` (verified numerically or against a build artefact / committed cache), `strong inference` (follows from verified facts but one step is not directly observed), `requires code inspection` (the manuscript is inconsistent; which side the implementation follows cannot be determined from this repository — it contains no source code).

---

## 1. Summary

| Dimension | Grade | Verdict |
|---|---|---|
| Physics & math correctness | **B−** | Core machinery (ansatz, marginal, SR/CG, exact solver) verified sound; the defects concentrate in the new CEM/temperature machinery. |
| Completeness (promise vs delivery) | **C** | Real QPU results now exist, but sample *quality* and *time* versus classical solvers — the two things the Overview promises — are both still unmeasured for the annealer. |
| Novelty & positioning | **narrow** | All three new contributions sit in occupied territory; the residual gap is real but small and inside one group's active programme. |
| Readability & writing | **C+** | Six defects a reader hits without looking for them; ~35 language errors; no abstract, no conclusions. |
| Reproducibility | **C−** | Seeds, error bars and a hardware paragraph are new and good, but the seeding sentence contradicts the committed caches, one of Fig. 12b's three curves has no data on disk, and no plotting script is committed. |

**Three critical findings** (F1–F3) undermine the interpretation of headline results. **F1**: the CEM validation's reference family is not the one the sampler realises, so the quoted RMSE cannot be read as CEM's error. **F2**: `auto_scale` nullifies the stated β_x → β_eff mechanism on the QPU. **F3**: the sparsity study's central claim is contradicted by its own committed data. All three are fixable with code that already exists.

---

## 2. Correctness — physics and mathematics

### 2.1 Verified correct (checked, not merely read)

- **Ansatz and marginal, Eqs. (13)–(16) (L240–257).** `Σ_h exp(−E_θ(v,h))` over `h ∈ {−1,+1}^{N_h}` reproduces Eq. (16) exactly, including the `e^{−a·v/2}` prefactor; the joint/marginal relation at L248 is stated correctly. *(confirmed)*
- **Exact TFIM solver, Eq. (28) (L594–601).** Verified by dense exact diagonalisation independent of the report's tooling: across `N = 3…12`, `h ∈ {0, 0.1, 0.3, 0.5, 0.9, 1.0, 1.5, 2.0, 3.0}`, `J = 1`, agreement is at worst **5.0×10⁻¹⁴** absolute. The report's own claim (N ∈ {4,6,8,10}, h ∈ {0.5,1,1.5}, < 10⁻¹³) passes on all 12 pairs. **There is no factor-2 error** — `ε(k) = √(J²+h²−2Jh cos k)` summed over all N momenta equals `−½ Σ_k ε_Bog(k)` with `ε_Bog = 2√(…)`. *(confirmed: `verify/tfim_e0.py`)*
- **β_eff algebra, Eq. (18) (L318–321).** `E_in = α E_θ`, `α = 1/β_x`, `β_eff = α β_hw` is internally consistent and `β_eff = 1/β_x` at `β_hw = 1` follows. Fig. 6b's rendered "ideal 1/β_x" curve does decrease, and the measured β_eff crosses 1 at each panel's optimum. *(confirmed)*
- **SR/CG machinery**, Eqs. (22)–(27), including the `O(N_s·N_params)` matrix-free product. *(confirmed; one presentational slip, M7)*
- **Model signs and framing**: TFIM/LRTFIM transverse fields; the positivity of the TFIM ground state; the Marshall transformation and — new and correct in this revision — its breakdown for `J₂>0` (L415, citing Richter_1994). `D_TV` (Eq. 17) and TTS (Eq. 1) are standard. The CEM validation's 480-draw design is arithmetically consistent (2 N × 4 h × 4 β_x × 5 seeds × 3 checkpoints). *(confirmed)*
- **No missing `\includegraphics` targets; all 15 acronyms are used at least once.** *(confirmed)*

### 2.2 Critical findings

---

**F1 — The CEM validation's reference family is not the one the sampler realises.** *(confirmed mathematically; magnitude on the actual instances: requires code inspection)*

*Finding.* The sampler (L318) scales the **joint** energy, so its visible marginal is `p_α(v) ∝ e^{−α a·v} Π_j 2cosh(α Θ_j)`. The validation (L365) instead fits β in the family `|Ψ(v)|^{2β} ∝ e^{−β a·v} Π_j (2cosh Θ_j)^β`. Because `Π 2cosh(αx) ≠ Π (2cosh x)^α`, the two coincide **only at α = 1** — and α = 1 is exactly where the report reports zero bias.

*Evidence.* With a perfectly calibrated estimator and zero sampling noise, the reference's own bias on the report's β_x grid is +0.29/0.00/−0.085/−0.108 (N=8) and +0.18/0.00/−0.082/−0.112 (N=12) in one run; across 24 random weight draws the induced RMS spans **0.008–0.19**, i.e. it is strongly instance-dependent and *can* reach the magnitude of the report's quoted RMSE (0.148 / 0.153). Note the reported RMSE lies *inside* that span rather than above its top — which itself shows a random-weight proxy overstates the effect on trained RBMs.

*Impact.* The quoted RMSE cannot be interpreted as CEM's accuracy until the validation is recomputed against the correct family on the actual checkpoints. Both qualitative conclusions are also predicted by the mismatch alone: "essentially unbiased near β_eff = 1" is a tautology (the families are identical there), and the "systematic overestimate in the high-temperature regime" has the sign and rough size the mismatch forces (at β_x = 1.5–2 the reference sits 0.08–0.11 *below* the true α).

*Fix.* Refit the ground truth as `p_β(v) ∝ e^{−β a·v} Π_j 2cosh(β(b_j + (Wv)_j))` — the marginal of the β-tempered joint — and re-derive L365 and Fig. 7 on the real instances. *(reproduce: `verify/cem_family.py`)*

---

**F2 — `auto_scale` nullifies the stated β_eff mechanism on the QPU.** *(confirmed from D-Wave's documented behaviour + L647)*

*Finding.* L258 attributes β_eff to rescaling `a, b, W` by a common factor before programming the device; L647 reports `auto_scale` **enabled**. `auto_scale` renormalises all biases and couplings to fill the solver's `h_range`/`j_range`, so a *uniform* rescaling of all RBM weights is divided straight back out and cannot change what the annealer solves.

*Impact.* The mechanism the whole temperature section rests on cannot operate on D-Wave as configured, and no QPU β_eff is measured anywhere to substitute for it.

*Fix.* Either disable `auto_scale` for the temperature experiments and say so, or record and report the applied autoscale factor and **estimate β_eff directly from the returned samples**. Do not claim that β_eff then reduces to the device's physical temperature: the sampled distribution also depends on the programmed energy scale, on `B(s)` and the freeze-out point, on the annealing dynamics, on embedding and chains, on analog control error, and on genuine departures from a Boltzmann form. D-Wave's `freezeout_effective_temperature` utility is the documented starting point.

---

**F3 — The sparsity study's central claim is contradicted by its own committed data.** *(confirmed: `verify/cache_budget_stats.py`)*

*Finding (a) — budgets are not matched, and the confound points the same way as the claimed effect.* In `cache_sparsity_ablation*.json`, the classical arm ran a uniform **300 SR iterations** at all four masks and all 5 seeds; the QPU arm ran **14–300**, with per-level means 147.6, 276.4, 155.2, **26.6** and counts `[31,300,205,176,26]`, `[297,300,185,300,300]`, `[15,133,300,28,300]`, `[44,25,18,14,32]` — budget deficits of **2.03×, 1.09×, 1.93×, 11.28×**.

*Finding (b) — at matched budget the QPU wins.* At sparsity 0.6836 (1.09× deficit) the QPU arm's mean relative error is **9.6 % against the classical arm's 19.6 %**; at 0.5586 (2.03×) it is **8.4 % vs 10.5 %**. The QPU arm is worse only at 0.8086 and 0.8789, where its realised budget falls to 52 % and 9 % of the classical one. So L482's claim that "real hardware sampling adds an extra penalty on top of the sparsity itself" has **no support at any level where the budgets are comparable** — and the report withholds precisely the QPU numbers that show this (per-level seed ranges 0.7–16.8 %, 4.3–20.2 %, 8.0–69.6 %, 34.4–87.4 %).

*Finding (c) — Fig. 12b's classical curve splices two different experiments.* Its four sparse points come from `cache_sparsity_ablation.json` (n_params 145/113/81/63 on coupler-pruned Zephyr masks), but its sparsity-0 point is a **dense 288-parameter biclique RBM from `cache_full.json`** — a different experiment, with no QPU and no floor counterpart — joined across a 0.55-wide gap containing no data, and carrying most of the figure's visual dynamic range. A comparable classical native-Zephyr point at sparsity 0.426 (3.28 % relative error) sits **unplotted in the same cache**.

*Finding (d) — the quoted floor numbers do not match the plotted floor.* L484 says the exact-ansatz floor "stays roughly flat at 1.1–1.8 %"; the plotted floor is **1.05/1.48/3.45/2.41 % per spin (0.82/1.16/2.70/1.89 % relative)** — it rises 3.3× and peaks at the third mask rather than staying flat. The accompanying "five to fifteen times larger than the floor" is exceeded at sparsity 0.682 (16.9×).

*Impact.* The section's headline conclusion, and the one element of it this audit rates genuinely new (the ansatz-floor decomposition), are both unsupported as presented.

*Fix.* Re-run the QPU arm to 300 iterations, or truncate the classical arm per (sparsity, seed) to the QPU's realised count, and state the matching rule in the caption; quote the QPU arm's means and seed ranges; either plot all three arms at sparsity 0 or drop the dense point (the unplotted native-Zephyr point at 0.426 is the natural replacement); and correct the floor description to the plotted values.

---

### 2.3 Major

| ID | Where | Issue | Confidence |
|---|---|---|---|
| M1 | **L213 (Eq. 10), L356 (Eq. 19)** | **The CEM conditional expectation carries the wrong overall sign under the report's own energy function.** With `E_θ = a·v + b·h + h·W·v` (Eq. 13, all plus signs, locked in by Eq. 16's `e^{−a·v/2}`) and `p ∝ e^{−βE}`, the field on `h_j` is `−βΘ_j`, so `⟨h_j⟩ = −tanh(βΘ_j)`. Verified by exact enumeration over `h ∈ {−1,+1}³` at β = 0.7, 1.0, 1.8. Fix: print `−tanh(βΘ_j)` (and `F(β) = Σ_j(h_{j,obs} + tanh(βΘ_j))²`), or flip Eq. (13) to `E = −(a·v + b·h + h·W·v)`. **Raise to critical if the implementation shares the sign**; the repository contains no source code, so this cannot be settled here. | confirmed (manuscript) / requires code inspection (implementation) |
| M2 | **L360 (Eq. 20), L362, vs L215–217 and Fig. 11a** | **The matching objective is described inconsistently across the document.** L215–217 uses the conditional expectation `⟨h_j⟩`; L360–362 defines `F(β)` against "actual samples" of `h_j`; Fig. 11a's legend says "binned average". The single-sample reading is **not ill-posed** — the population risk is `Var(h_j) + (m_j(β₀) − m_j(β))²`, so it is a consistent M-estimator (median β̂ → β₀ = 1.000 at N_h = 256) — merely high-variance. It does have a genuine degeneracy: when every observed `h_j` agrees in sign with `Θ_j`, `F` is monotone and a bounded optimiser returns its bound; at the report's own operating point (|Θ| up to ≈3, β_eff = 1.94 from Fig. 11a) this fires on ≈**24.8 % of draws at N_h = 16**. That is a *plausible* mechanism for the reported saturated draw — but the same simulation **refutes** the literal single-sample reading, since it predicts 120–200 saturated draws out of 480 against the 1 reported, consistent instead with ≈16–30 pooled draws. Fix: define `h̄_j` as the mean over `N_c` conditional draws, state `N_c`, and say which bound the outlier hit (an early, small-\|Θ\| checkpoint preferentially hits the *lower* bound, ≈20.6 %). Also fix the unbalanced parenthesis in Eq. (20) and the paragraph that opens with a comma. | confirmed (`verify/cem_objective.py`) |
| M3 | **L602** | Two false statements about the parity sectors, which must be split by regime. (a) "which sector wins depends on N and h": a scan of 12.5 M (N,h) pairs (N = 2…500, h ∈ [10⁻⁶,10⁴], J=1 — note the scan does not include h = 0 exactly, where the two sums coincide) found **no** case where the periodic sum is lower, so the `min()` is inert for J>0. (b) The second sum is not "the odd-parity sector energy" in general: for **h < J** it equals the lowest odd-parity state *exactly* (to 10⁻¹⁴ — the absolute value in `ε(0)=\|J−h\|` reproduces the occupied unpaired k=0 mode), while for **h > J** it lies exactly `2(h−J)` below it, because that mode carries a signed energy and the parity constraint forces it occupied. | confirmed (`verify/tfim_e0.py`) |
| M4 | **L91 (Eq. 2), L593** | **No boundary condition, and no `J>0`/`h≥0`, is ever stated**, yet Eq. (28) is periodic-specific. `\|E_OBC − closed form\|` at N=12 is 0.871 (h=0.5), 0.397 (h=1.0), 0.186 (h=1.5) — far above any variational error quoted. For an antiferromagnetic ring with **odd N** the formula returns an energy strictly *below* E₀ (N=5, J=−1, h=0.3: −5.114 vs −3.713), because it is invariant under J → −J. | confirmed |
| M5 | **L144 (Eq. 8)** | The problem Hamiltonian is broken, visibly in the PDF: a stray `=` after the first sum; an unrestricted double sum that includes `i=j` and double-counts pairs, contradicting Eq. (9) five lines later; `σ_z^{i}` mixed with `σ_z^{(i)}`. | confirmed |
| M6 | **L607** | False variational-bound claim: the principle bounds the exact `⟨H⟩_Ψ`, not a finite-sample estimate, and a minimum over noisy iterations is biased *downward*. The caches make this concrete — `min(energy_history)` beats the reported `E_final` in 110 of 120 records. | confirmed |
| M7 | **L662 vs L679** | Appendix Step 2 asserts `(1/N_s)(Ō^TŌ)_kl = S_kl − λδ_kl`, false given the unregularised `S_kl` two lines earlier; `S` is silently redefined mid-proof. Same collision at L548, L575, L653. | confirmed |
| M8 | **L260** | RBM definition inverted: "no **inter**-layer connections are allowed" — an RBM forbids *intra*-layer connections. | confirmed |
| M9 | **L417–421** | The average sign is **identically 1 for the report's own ansatz** (whose amplitudes are strictly positive per L406), so as written it measures nothing about their model; it must be stated as evaluated on the exact ED ground state. Still mis-cited to `He_2017` (TFIM boundary effects) while `Troyer_2005` sits uncited. | confirmed |
| M10 | **L294 / L324 / L275** | Three broken cross-references. `\autoref{anneal_schedule}` points the report's only sampling-quality result at Figure 3a, three pages earlier (`aux`: `{{3a}{7}}`). `\label{sec:exper:temp}` trails the body of §4.2.1, so both call sites print "subsubsection 4.2.1" — and L209's reference sits inside a `\paragraph` with the identical title. `\label{fig:embedding-zephyr}` precedes its `\caption{}` (`aux` records `\caption@xref {??}`). | confirmed |
| M11 | **L77** | Figure 1's caption contradicts its own plot: "GPU solvers dominate for N ≳ 100", but at N≈112 SA (CPU) ≈4×10¹ ms beats SA (GPU) ≈1.2×10² and VeloxQ ≈1.1×10². The body text at L60 is the correct claim. | confirmed |
| M12 | **L484 vs Fig. 12b axis** | **Text and figure plot different quantities.** The axis label "Energy error per spin \|ε\|/N" is **correct** — decoded markers divided by `\|E_exact\|/N = 1.27529` reproduce the cached means to ratio 1.00000 — while the prose quotes plain *relative* errors. The two differ by a factor 1.275, so the percentages at L484 cannot be located on the figure. (Deleting the "/N", as revision 2 of this audit and the reviewer critique both proposed, would have made the figure wrong.) Fix: plot relative error, or restate the prose in per-spin units, and say which in the caption. | confirmed |
| M13 | **L500** | The caption "The dotted line marks the exact-ansatz floor" is **ambiguous rather than wrong**: the floor is dotted, but so is a separate grey vertical "native hardware floor" line the caption never mentions. Name both. | confirmed |
| M14 | **L517 vs L434–436** | Two different seed-aggregation standards three pages apart: median-over-seeds with IQR and divergences retained as failures (Fig. 10) versus "best of 3 seeds" (Fig. 13b). Best-of-N is upward-biased, and biased *more* for the high-`n_parallel` arm, so part of the reported speedup is an estimator artefact. Seed-resolved versions of that figure exist unused on disk. | confirmed |
| M15 | **L323 / L349** | "clearly illustrates that the sampler temperature is problem dependent" overstates the evidence: optimal β_x ≈ 0.580, 0.560, 0.480 for h = 0.5, 1.0, 2.0 — a ~17 % spread over a 4× change in h, inside a sweep window only 0.40–0.60 wide, and in the h=0.5 panel the 5000-step curve is still decreasing at the right edge, so that optimum is truncation-limited. | confirmed |
| M16 | **L233** | The method is labelled **VQE**, but no parametrised quantum circuit exists anywhere; this is quantum-assisted VMC with a neural-network ansatz. | confirmed |
| M17 | **L106/L116/L127 vs L411; L246/L256** | Pauli-vs-spin-½ convention never stated and silently mixed (Pauli Hamiltonians, `S^z` in the Marshall transformation — a factor 4); the hidden-unit domain `h_j ∈ {−1,+1}` is never stated although both the `2cosh` factorisation and the `tanh` conditional require it. | confirmed |
| M18 | **L592, L121** | `\gls` inside a section heading corrupts the PDF bookmark (`report.log` hyperref warning; bookmark #36 reads the literal glossary key "tfim ground state solving in O(N)"). Wrap in `\texorpdfstring`. | confirmed |
| M19 | **bib.bib** | `Paw\l{}ł` renders as "**Pawłłowski**" (correct two entries later); three undefined month macros (`Sept`, `June`) leave two entries monthless; `unsrt` lowercases unbraced titles, printing "frustrated **$j_1$-$j_2$** heisenberg antiferromagnet"; entry [11] prints a raw `&#x2014;` and has empty author and year; three entries never cited (`veloxq` — though VeloxQ is configured at L647 and appears in Fig. 1's legend; `Troyer_2005` — whose result L406 asserts uncited; `mpg`). | confirmed |

### 2.4 Minor (selected)

QUBO expanded as "quadratically binary unconstrained optimization" (L27, printed on page 2; correct is *quadratic unconstrained binary optimization*) · `Ψ = √(Σ_h e^{−E})` is non-standard versus Carleo–Troyer and the cited Gardas et al. (`Ψ = Σ_h e^{−E}`), which changes the log-derivatives the report says are taken analytically from that reference — state the choice (L246) · `D_TV` defined against a `ν` given only up to proportionality (L289) · LRTFIM without boundary condition or Kac normalisation, so energy per site diverges for `α ≤ 1` (L98) · `α` carries three unrelated meanings and `β` a fourth in Fig. 1's caption · σ_y declared but absent from the equation it follows (L142) · annealing schedule without the vendor's factors of ½ (L149) · CEM framed for **SRBMs** (visible-visible couplings) while the ansatz is a strict RBM, and SRBM is never defined (L209–211) · "not possible" overstates when the free-fermion mapping fails — the XXZ chain is Bethe-ansatz integrable and its Δ=0 point *is* free-fermion (L604) · Lanczos described as returning only the lowest eigenvalue (L605) · spurious "thermodynamic limit" on the `h→∞` uniformity statement (L296) · two of three coupler types described indistinguishably (L189–191) · `f(x^n)` / `q(x_n|x*)` slips inside Eq. (12) (L225) · `W_{ij}` vs `W_{ji}` transposed between L256 and L356 (only one can match `h·W·v`) · `c_j` vs `b_j`, hidden count as `N`/`N_h`/`M`, undefined conditioning label `C` · `n_parallel = 4` in the worked example and panel (a) but `{1,3,5}` in the only panel with data (L504 vs L517) · caption says "solid markers" where the legend swatch is unfilled (L510) · italic unit symbol `$20\,\mu s$` and the document's only overfull box (L647) · duplicate `\usepackage{graphicx}` (L7, L12) · stray `*` in the appendix divider (L649).

Language errors, verified individually: L54 "physical **und**" · L74 "corresponds a" · L83 "results return by" (plus `\cite{}\cite{}` printing "[3][4]") · L282 "properties **or** samplers" (the opener of §4) · L323 "inpact" · L364 "minized" · L450 "annealing **progress**" · L452 four in one paragraph ("performers reasonably", "is creating according", "constructe", "on quantum annealer") · L504 "experimentacally", "parallel approaches convergence faster" · L586 "matrix.Computing" · L607 "Gibb's" · L611 "JAX transformation require function" plus straight double quotes · L314/L323/L343 "total **variational** distance" against the report's own correct definition at L285 · plus articles, agreement, dangling participles, `Jax`/`JAX`, `e.g.` spacing and `J1J2` vs `$J_1$-$J_2$` at L53, 138, 142, 156, 221, 243, 285, 290, 294, 296, 318, 398, 406, 409, 524, 527, 604–605, 625, 644.

---

## 3. Completeness — promise vs delivery

### 3.1 What D-Wave data exists

Two experiments touch real hardware, and both are genuine: the **sparsity ablation** (Fig. 12b — N=16, h=1, Zephyr, four masks, 5 seeds, QPU vs classical, plus an exact-enumeration floor) and **parallel embeddings** (Fig. 13 — `K_{8,8}` on Pegasus, `n_parallel ∈ {1,3,5}`, energy vs cumulative QPU access time). Everything else D-Wave-flavoured is illustrative. Together they establish something narrow but real: **an RBM can be trained end-to-end from D-Wave samples at N=8 and N=16, and simultaneous parallel embeddings do not destroy training.**

### 3.2 Critical gaps

1. **No distribution-quality measurement for QPU samples** (L283–316): the entire Sampling Quality section is SA/Metropolis/Gibbs/LSB, so the device the report is *about* is the one sampler whose quality is never measured — even though at N=8, M=8 the exact `|Ψ|²` is enumerable and one QPU call per point is cheap.
2. **No QPU-vs-classical time comparison** (L83, L504–522, L647): the only time axis plots QPU-parallel against QPU-serial. VeloxQ/FPGA and `dwave-neal` are configured at L647 and produce zero results; Eq. (1)'s TTS metric is used only for prior work.
3. **"Computationally hard problems" is not delivered** (L83): the largest system in this work's results is **N=16**; every instance is exactly enumerable or diagonalisable — the sparsity ablation enumerates 2¹⁶ states.
4. **No Discussion or Conclusions section** (structure runs L646 → L651): the question posed at L49 is never answered and the experiments are never drawn together.
5. **The sparse-embedding section never tests its own hypothesis** (L450–502): no comparison against a dense, chain-embedded RBM at equal N on the same QPU, and no qubit-count or QPU-time saving from going chain-free is quantified.

### 3.3 Major gaps

- **Hardware β_eff is never measured** (L258 → L317–352), and F2 means it cannot be inferred either.
- **CEM is never applied to the QPU**, though L219 asserts it can be; the matching figure does not even name which sampler produced the observed hidden units.
- **LRTFIM and XXZ appear in zero results** (L95–100, L111–119); L604 justifies exact diagonalisation by invoking long-range interactions that never appear.
- **Single QPU operating point** (L647): 20 µs anneal, `auto_scale` on, default chain strength, no sweep of either — precisely the trade-off the goal statement is about.
- **No headline accuracy number for QPU-driven training**: Fig. 12b quotes error percentages only for the classical arm; Fig. 13b's y-axis is raw energy with no relative error and no exact baseline.
- **Parallel-embedding controls**: no statement whether `num_reads` was divided by `n_parallel` to hold total samples fixed; no chain-length or chain-break statistics per copy; no independence check between simultaneous copies.
- **Statistics reported unevenly**: present for the CEM validation, the convergence figure and the TFIM ordering figure; absent for Figs. 5, 6, 8, 12 (seed count never stated in text) and 13.
- **Missing hyperparameters**: numeric η and λ, CG tolerance, LSB timestep/pumping/noise, and the "sampling floor" defined only inside captions.
- **Framing contradiction**: the report shows the positive ansatz failing on the frustrated chain beyond J₂/J₁ = 0.5 — the "hard" problems that motivate the QPU comparison — and never says which hard-but-stoquastic class remains as the target (`grep stoquastic` → 0 hits).

---

## 4. Novelty and positioning

### 4.1 The three new contributions, and the occupied territory around them

| Contribution | Verdict | Prior art |
|---|---|---|
| **CEM β_eff estimator validated against a KL-argmin ground truth** (L353–401) | **Pre-empted** | Kubo & Goto, arXiv:2512.02323 — CEM's inventors — already define `β_eff = argmin_β D_KL(P_S‖B_β)` and validate CEM against it. |
| **Sparse chain-free RBM fitted natively to Zephyr** (L449–502) | **Incremental** | Architecture: Park, Chancellor, Griffin, Kendon & Stepney, "Benchmarking the D-Wave Quantum Annealer as a Sparse Boltzmann Machine" (UCNC). Accuracy-vs-sparsity: Golubeva & Melko, PRB 105, 125124 (2022); Pilati & Pieri, PRE 101, 063308 (2020). The chains-bias-sampling motivation: Marshall, Di Gioacchino & Rieffel, PRR 2, 023020 (2020). Genuinely new: only the exact-enumeration ansatz-floor decomposition — and per F3(c,d) it is the one arm with no committed data and quoted numbers that do not match its own figure. |
| **Parallel embeddings to cut QPU access time** (L503–522) | **Pre-empted** | Standard practice; canonical reference Pelofske, Hahn & Djidjev, "Parallel quantum annealing", Sci. Rep. 12, 4499 (2022), with ≥4 further demonstrations, two specific to Boltzmann machines. |

**The sampling-quality benchmark also sits in occupied territory.** Berns, Rodrigues, Finocchio & Mentink, *Predicting sampling advantage of stochastic Ising machines for quantum simulations*, **Phys. Rev. Applied 25, 024085 (2026)**, arXiv:2504.18359 — verified in every field — benchmark a parallel Ising-machine sampler against Metropolis–Hastings on **pre-trained RBM neural quantum states** (2D Heisenberg antiferromagnet, up to 484 spins, α ∈ {2,3,4,8}), measuring steps-to-iso-accurate variational energy and projecting a 100–10 000× hardware speed-up. That is structurally the same experiment class as L283–316. The report's genuine differentiators — which must be stated explicitly rather than left implicit — are the **metric** (exact-enumeration `D_TV` rather than autocorrelation time), the **sampler class** (non-Boltzmann LSB with unknown β_eff rather than an exact Gibbs sampler at T=1), and the **inclusion of real QPU samples**. Berns runs no sampler inside a training loop and the words "temperature", "beta" and "bifurcation" do not occur in it. Also relevant and uncited: an SB/CIM-class sampler already drives RBM/DBN learning in Phys. Rev. Applied (DOI 10.1103/6c63-cmgy, Mar 2026), and Goto & Ohzeki, JPSJ 94, 034002 (2025) do in-training-loop temperature calibration for RBMs on a real QPU.

### 4.2 What remains open — and how narrow it is

The literal gap survives: **no published work puts a simulated-bifurcation-class sampler with per-iteration effective-temperature correction inside an NQS/VMC optimisation loop.** Positive evidence of openness: Kubo & Goto has zero citing papers in Semantic Scholar; arXiv abstract searches for "simulated bifurcation" ∧ "neural quantum", for "Langevin simulated bifurcation", and for "neural quantum states" ∧ "effective temperature" all return nothing.

But it is a gap inside an active programme, not a frontier. Mentink co-authors **both** Berns (PRApplied 2026) and Chowdhury et al. (arXiv:2512.24558, p-bit sampler inside SR training, 2D TFIM to 6400 spins), and Berns' only citation is Chowdhury — one group, two papers, moving in this direction. Consequently the differentiator cannot be the hardware class ("trained by an SB-class sampler" is doubly taken) but must be the **mechanism**: an unknown, instance-dependent, drifting β_eff, its CEM correction inside the SR loop, and a quantitative tolerance statement for how far from Boltzmann a sampler may be before SR fails. Second still-open item, now feasible because real QPU data and a documented configuration exist: a **joint quality-and-cost benchmark** across D-Wave, LSB and GPU MCMC on identical RBM Born distributions at matched budgets.

### 4.3 Missing citations

Berns et al. 2026 and the six prior-art items above; Carleo & Troyer, Science 355, 602 (2017) (the ansatz itself); Goto et al., Sci. Adv. 5, eaav2372 (2019) (SB, uncited at L201–206); King et al., Science 388, 199 (2025) (the "2025 D-Wave claim" at L49); Metropolis 1953 / Hastings 1970 (L223 cites a blog); Kirkpatrick 1983 (the SA subsubsection has no citation at all); Troyer & Wiese, PRL 94, 170201 (2005) (in `bib.bib`, uncited). Rather than a reference count, the missing **categories** are: NQS foundations, quantum-assisted Boltzmann-machine training, annealer effective-temperature estimation, Ising-machine samplers for quantum simulation, NQS sign-structure literature, and the embedding/sampling-bias literature.

*(One correction carried over: Gardas, Rams & Dziarmaga, PRB 98, 184304 (2018) is confirmed — DW2X/2000Q, RBMs to 64×64 — but it performed **no** β_eff calibration, only a heuristic adjustment of the initial inverse temperature. CEM-style instance-wise calibration on modern hardware therefore is differentiating.)*

---

## 5. Readability

**Six defects a reader hits without looking**, all confirmed in the compiled PDF: the sampling-quality result points at "Figure 3a" (L294); the QUBO expansion is wrong on page 2 (L27); Eq. (20) prints an unbalanced parenthesis (L360) followed by a paragraph opening with a comma (L362); Eq. (8) prints a stray `=` (L144); the bibliography prints `&#x2014;` (bib.bib L164); a PDF bookmark reads "tfim ground state solving in O(N)" (L592).

**Structure.** No abstract. No Discussion/Conclusions — `grep` for Conclusion/Discussion/Summary/Outlook returns zero. No `\date`, so `\maketitle` stamps the build date and it changes on every recompile; pin it deliberately. Self-reference drifts between "this work", "this article" (L527) and "this chapter" (L524) in an `article` class. The JAX tutorial (L608–645) and the Appendix (L651–707) read as thesis material. **Figure 9 (`fig:tfim_ordering`) is an orphan** — "Figure 9" appears exactly once in the PDF, in its own caption — and floats into the Marshall paragraph, which is about a different model. Three passages say "the left/right subfigure" while the correct labels sit unused two lines below (L364, L504). 23 labels are never referenced; 53 of 94 image files are never included, including a duplicate `sparse_graph_construction/` tree.

**What reads well.** The SB/LSB/CEM exposition (L201–219); the SR section and the Appendix's two-pass derivation; the sparse-mask construction algorithm; the honest labelling of previous-work figures; the volunteered limitations at L484 and L421; and Fig. 10's divergence accounting, which is better practice than most published NQS papers.

---

## 6. Reproducibility

Genuinely improved: 5 seeds per condition with 95 % CIs (L380), median-over-seeds with IQR bands (L435), Optuna tuning on a disjoint set (L437–438), divergent runs retained as failures (L440–443), and a hardware/software paragraph naming solvers, anneal time, `num_reads`, `auto_scale`, embedder and baselines (L646–648).

Gaps, several of them newly identified against the committed caches:

- **The seeding sentence contradicts the data.** L647 says runs are seeded "via `np.random.randint` feeding `jax.random.PRNGKey}`". Every cache key ends in one of five **fixed** seeds `{42, 123, 456, 789, 1234}`, none of which appears in `report.tex`. Beyond that, `np.random.randint` provides no reproducibility at all unless a master seed is recorded. Report: the master seed, the per-experiment seeds, and how JAX keys are derived from them.
- **One of Fig. 12b's three curves has no data on disk.** The exact-ansatz floor is in none of the repository's five JSON caches, and **no plotting script is committed anywhere** — so the classical and QPU arms are reproducible and the floor is not.
- **Cache semantics are trap-laden and undocumented**: the SR iteration count is not a field but `len(energy_history)`; the seed lives only in the key; field 2 of a key means target sparsity in the ablation caches but α in `cache_full.json`; and `E_final` is a fresh re-evaluation differing from `energy_history[-1]` by up to 6 % of `|E_exact|`.
- Missing: numeric η, λ, CG tolerance, LSB settings, sample counts for five figures, and any data/code availability statement.

---

## 7. Verdict and recommendations

*(Section 7 mixes audit findings with expert judgement. The findings above are verifiable; the venue, effort and risk estimates below are opinion.)*

**Not submittable today**, but the distance is weeks, not months. The new contributions cannot carry a paper as framed — all three sit in occupied territory — so reframing is mandatory. The defensible headline is the **mechanism**: LSB with per-iteration CEM correction inside the SR loop, supported by a quantitative sampler-bias tolerance analysis, explicitly differentiated from Berns et al. and Chowdhury et al. That needs no QPU time. The QPU work becomes a credible second half once F2 and F3 are resolved and a QPU `D_TV` curve plus one matched-cost time comparison are added.

### P0 — before anyone outside the group reads it (hours)
1. Fix Eq. (8) (L144); the Eq. (20) parenthesis and comma-paragraph (L360–362); the RBM definition (L260); the QUBO expansion (L27); the `&#x2014;`/empty-field bibliography entry.
2. Repair the three broken references (M10) and convert L193–199 to `subfigure` with `fig:`-prefixed labels so the wrong-reference bug cannot recur.
3. Reference or delete Figure 9; fix Fig. 1's caption (M11); resolve the text-vs-figure unit mismatch in Fig. 12b (M12) and name both dotted elements (M13).
4. Full proofread pass over §2.4.

### P1 — before any submission (weeks)
5. **F1**: redo the CEM validation against the marginal of the β-tempered joint, on the real checkpoints; fix the sign (M1) and the objective's description (M2), stating `N_c`.
6. **F2**: disable `auto_scale` for the temperature experiments or record its factor, and estimate β_eff directly from QPU samples.
7. **F3**: re-run the sparsity comparison budget-matched; quote the QPU arm's numbers and seed ranges; fix the spliced classical curve; correct the floor description; commit the floor's data and the plotting scripts.
8. State boundary conditions and validity on Eqs. (2) and (28); correct L602 by regime or drop the inert `min()`; fix the Appendix `S`/`S+λI` collision and the L607 bound claim.
9. Add: a QPU `D_TV` curve at N=8; one matched-cost QPU-vs-classical time figure; median-with-IQR for Fig. 13b; an experimental-protocol table; an abstract; a Discussion/Conclusions section answering L49; a data/code availability statement naming the caches, solver IDs and seeds.
10. Add LRTFIM/XXZ results or cut those subsections; compress the JAX section; add the missing citations of §4.3 and reframe the sparse/parallel work as method notes with their prior art.
