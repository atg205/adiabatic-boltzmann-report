# Audit: *Toward Quantum Competitiveness in Adiabatic Quantum Computing: A Comparative Study of Variational Algorithms* (`report.tex`)

**Revision 11** — 2026-08-25. A verification pass, not a new audit. Every finding of revisions 8–10 was re-checked against the current manuscript; **the closed ones have been deleted from this document** and survive only as the one-line record in §3, so what remains below is the open list and nothing else.

*Provenance of this document.* Revision 8 was a full eight-lens re-audit. Revision 9 corrected three errors of revision 8 that had reached a published state — a stale `auto_scale` blocker, a reproducibility verdict formed from an out-of-date checkout, and several "missing" items that were in fact present. Revision 10 corrected revision 9 after a second review round: it rewrote the clock finding on verified implementation code, downgraded the scaling claim from proven artefact to confounded, withdrew a sub-finding, and refuted — with the indexing arithmetic — a proposed blocker about a supposedly forward-looking validation window. Each correction is recorded in the finding it touches. The separate changelog and review files have been removed at the author's request; this file is now the whole audit.

**Target.** `report.tex` at **`9917b34`** ("small text fixes") — 796 lines, 27 compiled pages. Bibliography: 29 records in `bib.bib`, 28 of them cited and printed. Verify with `wc -l report.tex` (→ 796) and `git log -1 --format=%h -- report.tex` (→ `9917b34`). Implementation repository: `iitis/adiabatic-boltzmann`, last inspected at `a4b0f2006`.

**Verdict: 17 of 24 earlier findings are verified closed; 7 remain, and 2 new findings are added below (O9, O10), giving 9 open.** The three post-audit commits (`5ab5210` "fixed audits findings", `a8d03fc`, `9917b34`) resolved every blocking finding except one, and did so properly rather than cosmetically — the fixes were checked against the text, not taken from the changelog. What is left is one substantive contradiction, one missing experiment, and seven items of provenance, style and polish — including a bibliography that prints all 63 authors of one reference.

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

### O2 — No *matched* QPU-versus-classical sampling-quality benchmark *(confirmed)*

A QPU `D_TV` measurement does exist — the auto-scale subsection reports `D_TV ≈ 30 %` at the optimal setting with `auto_scale=False`. What does not exist is a **matched** comparison: the Sampling Quality section (L281–320) contains zero mentions of the QPU, and the auto-scale figure uses a different instance, sample count, sampling floor and effort axis, so the two cannot be read against each other. CEM is deployed on QPU samples but never validated on them, and no β_eff is reported for any QPU run that uses it. This is the paper's original stated aim and the largest remaining gap in substance. **Fix:** add a QPU `D_TV` curve at N=8 against the enumerable exact distribution, on the same axes as the classical benchmark.

### O3 — ε-sensitivity is acknowledged qualitatively but never quantified *(confirmed)*

The report does flag the robustness problem in words — the abstract calls the trend "too sensitive" to the criterion parameters and the Conclusion says the result is "not robust" to them. What is missing is the number behind that admission. The historical check of this methodology gives, for Zephyr(+CEM):

| ε | fitted exponent |
|---:|---:|
| 0.05 | −0.493 |
| 0.10 | −0.199 |
| 0.15 | +0.161 |
| 0.20 | +0.201 |

**The sign flips between ε = 0.10 and ε = 0.15** — i.e. between "the annealer improves with size" and "it degrades" — and ε = 0.1 is what the paper reports. **Fix:** publish a sensitivity table over ε ∈ {0.05, 0.10, 0.15, 0.20} with validated seed counts, medians and fitted exponents. (An earlier revision of this audit suggested ε ∈ {0.01, 0.1}; that grid does not bracket the sign change and would not settle the question.)

### O4 — Figure 1(a)'s data provenance is undisclosed *(confirmed)*

Its points were recovered from the published figure's vector paths rather than from underlying data — the generating script says so, the caption does not. `grep` for "recovered from", "digitis", "re-extracted" in `report.tex` returns nothing. **Fix:** one clause in the caption.

### O5 — The availability statement names no commit *(confirmed)*

L717 gives the repository URL with no commit hash or DOI, for a repository that moved 13 commits between the two states this audit pinned and 82 since the checkout it was first judged from. QPU access dates are now recorded (2026-05-11 to 2026-08-10) — that half is fixed — but library versions remain unpinned. **Fix:** pin a commit hash or mint a Zenodo DOI, and pin versions in `requirements.txt`.

### O6 — LaTeX structure *(confirmed)*

No `\appendix`, so the appendix prints as a numbered section with equation numbering running on; no `\date{}`, so the title page stamps the build date and changes on every rebuild. `\lstset` is present, and the coloured link boxes are gone — though via `\usepackage[hidelinks]{hyperref}` rather than a `\hypersetup` call, so an earlier description in this audit was imprecise. **Fix:** add `\date{...}` with a fixed date; add `\appendix` before the appendix section, and `\numberwithin{equation}{section}` if equations should renumber as A.1, A.2; and retitle `\section{Appendix}` to describe its contents, or it prints as "A Appendix".

### O8 — Different timing boundaries are still described as directly comparable *(confirmed)*

An earlier revision of this audit asked for "one sentence naming both boundaries". That sentence now exists, and is good: L558 states that the classical series are timed by a host-side timer around the sampler call with JIT compilation excluded via a separate warm-up call, while the D-Wave series use the device-reported `qpu_access_time` (programming, anneal, readout) with network latency, queueing and one-time embedding excluded — and it further discloses that for the CEM series the host-side β_eff estimation is added on top, "rather than being the same kind of measurement".

What remains is the tension with L560, where the shared y-axis is said to make "absolute scale stays directly comparable". A common numerical axis does not reconcile different system boundaries. **Fix:** one clause, e.g. "the panels share a common numerical y-axis, but host-side classical sampler timings and device-reported QPU access times use different system boundaries and should not be read as end-to-end-equivalent."

### O9 — Build, render and notation polish *(confirmed)*

The build is free of undefined citations and references, but still reports: **three** `Token not allowed in a PDF string` warnings from the maths `$\epsilon$` in the heading "Time-to-$\epsilon$ across solvers", which strips the symbol from the PDF bookmark (fix with `\texorpdfstring`); and an **Overfull `\hbox` of 34.76 pt** in the sampler-parameter table (L701–711), which visibly runs into the right margin (fix with `tabularx`, a line break, or a smaller face). In the text: `$beta_{eff}$` at L360 is missing its backslash and prints as an italic product; `D_{TV}` and `D_\mathrm{TV}` are both in use, including within the same subsection; and L466 carries two editorial slips, "the the best possible" and the incomplete "the relative not only depends".

### O10 — The bibliography does not use author truncation, and its style does not match the intended look *(confirmed)*

`unsrt` prints every author of every entry. Reference **[1] (`King_2025`) therefore lists all 63 authors in full**, running to most of a column, where it should read "A. D. King *et al.*". Nothing in the current setup will ever truncate an author list.

The intended target is the APS/REVTeX look: initials before surname, sentence-case title in roman, the journal name hyperlinked, **bold volume**, first page only, year in parentheses — e.g. `A. D. King et al., Beyond-classical computation in quantum simulation, Science 388, 199 (2025).` The current output differs on every one of those points: full given names, italic journal, `volume:page, Month Year`, and the DOI on a separate line via a hand-added `note={\url{...}}` in each entry.

Both target styles are installed here (`apsrev4-2.bst` and `biblatex-phys` were both found in the TeX tree). **Recommended fix**, given the document is `article` rather than REVTeX:

```tex
\usepackage[backend=biber, style=phys, biblabel=brackets,
            giveninits=true, maxbibnames=3, minbibnames=1,
            doi=true, eprint=true, url=false]{biblatex}
\addbibresource{bib.bib}
...
\printbibliography
```

`maxbibnames=3` is what produces "et al."; `style=phys` gives the bold-volume APS layout, and it reads the real `doi`/`eprint` fields, so all thirteen `note={\url{...}}` hacks can be deleted. `apsrev4-2.bst` produces the same look but emits REVTeX-only macros (`\bibinfo`, `\bibfield`, `\eprint`), so it needs `revtex4-2` as the document class or stub definitions — the biblatex route is the lower-risk one here.

---

## 2. Priorities

1. **O1** — the only remaining contradiction between the text and committed data, and the largest credibility risk. Prefer disclosure over deletion: say that a preliminary QPU arm was run but is not reported because its 14–300 iteration budget was not matched to the uniform 300-iteration classical protocol.
2. **O2** — the paper's stated aim; needs an experiment, not an edit.
3. **O3** — an exponent whose sign flips inside the plausible ε range, with only a qualitative caveat in the text.
4. **O4, O5, O6, O8, O9, O10** — edits rather than experiments; the bibliography switch (O10) is the largest of them at perhaps an hour.
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
| M1 | Energy caption claimed "the same validated-convergence cells" | The phrase is still there, but it is now true: the regenerated time and energy figures use the same classical cells, and their five sub-20/20 annotations (16/20, 17/20, 17/20, 18/20, 19/20) match exactly. |
| M2 | Fig. 4(a) caption wrong by a factor of two (24 vs 12 units) | Caption corrected. |
| M3 | Hardware paragraph contradicted itself about simulated annealing | Now states SA runs on the JAX/GPU path and that "a separate `dwave-neal`-based SA implementation also exists in the codebase but is not used for any result in this paper". |
| M4 | Benchmark did not state its problem | L558 now gives the hidden-unit count ("N hidden units, matching the visible count") alongside the TFIM, h=0.5, seeds and protocol. |
| M5 | Coverage-gap sentence | Removed. |
| M6 | Sparsity floor shape and the "8–17×" band | Recomputed rather than deleted: the floor is now reported from medians (0.99 % → 2.44 %, a ≈2.5× rise) and the classical-to-floor gap as 9.7–17.7×. |
| M8 | Parallel-embedding numbers misdescribed | L487 now states the values are "each run's total recorded QPU time over its full 150-iteration budget, not the time at which it actually reached the energy plateau", and discloses that 2 of 3 seeds diverged. |
| M10 | Thirteen sections uncited; foundational references absent | Bibliography went from 16 to **29** entries, adding `Carleo_2017`, `King_2025`, `Goto_2019`, `Marshall_1955`, `Metropolis_1953`, `Hastings_1970`, `Kirkpatrick_1983`, `Geman_1984`, `Benedetti_2016`, `Pelofske_2022`, `Sorella_1998`, `Heisenberg_1928`, `Voigt_2000`. |
| M13 | Seeding protocol non-reproducible and contradicted by the caches | `np.random.randint` sentence removed; seeds stated. |
| M16 | `auto_scale` causal claim was a temperature confound | "dramatically worsens sampling performance" removed. |

| M7 | Legend box occluding three of four floor markers | **Verified closed:** the legend is now outside the axes on page 15 and all four exact-floor markers are visible. *Residual:* `figures/sparsity/sparsity_ablation_qpu_vs_classical.png` is older than the PDF (7 August versus 25 August) and still shows the occluding legend — regenerate or delete it so the repository does not carry two visually different versions of one figure. |
| O6 (was M11) | `Mehta_2025` missing its article number | Now carries `pages={032616}` and prints `Physical Review A, 112(3):032616`. |
