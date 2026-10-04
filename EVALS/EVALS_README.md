# EVALS_README — Every Evaluation, What It Measured, and What It Failed To Establish

Five layers of evidence are used in this project. **They must never be mixed.** Each layer answers a different question, and a result from one layer cannot substitute for another.

| Layer | What it actually measures | What it can support | What it cannot support |
|---|---|---|---|
| Historical prediction | Real labels on real old posts | Discrimination and error on the held-out set | Causal effect of rewriting |
| Fact / identity safety | Sources, numbers, identity, rules | That certain errors were found or blocked | That nothing was missed |
| Automatic judge preference | A model's choice under given dimensions | That one offline evaluation tool preferred X | Real community preference |
| Human feedback | What an actual reviewer wrote | That person's genuine reaction | Statistics on incomplete samples, group representativeness |
| Online feedback | Real post-publication exposure and interaction | — | **Never observed in this project** |

A sixth, retrospective layer — the reviewer's methodological critique of the whole design — is in `REPORT/Methodology_Review_and_Redesign.md`. It is a design argument, not an experimental result.

---

# Round 1 — Historical evaluators and the generation ladder

## E1 · Historical prediction (the only layer with real held-out labels)

**What it tests:** can high-performing posts be identified from pre-publication information only?
**Primary metric:** Average Precision (AP), chosen over accuracy because the positive class is a ~24.7% minority. Precision / Recall / F1 and accuracy reported alongside; ROC-AUC and Brier as supporting measures.
**Baseline:** E0 lazy (always predict non-high-performing) and E0 constant prior. The lazy baseline's 0.753 accuracy is exactly the trap the course warns about.
**Design:** temporal splits; thresholds frozen from development data before Final; author-clustered bootstrap for intervals.

**Result (Final, n=348):** E2 TF-IDF **AP 0.552**; E4 semantic embedding **AP 0.585**; both clearly above the 0.247 lazy baseline. E2's AP increment over the prior bootstrap interval ≈ **[0.219, 0.405]**.
**Limitation:** the signal may be carried by topic, terminology, resource links, or unobserved news. Clustering adjusts for some sample dependence — it does not remove exposure confounding, and it does not guarantee future generalisation.
**Files:** `evaluator_results.csv`, `evaluator_dev_results.csv`, `evaluator_bootstrap.json`, `E*_final_predictions.csv`.

## E2 · LLM historical classification on a fixed 80-post subset

E5a zero-shot / E5b few-shot / E5c retrieval, compared with E2 and E4 **on the same 80 posts** (only 11 positive). This subset must not be ranked against the 348-post results.

| Method | P | R | F1 | AP |
|---|---:|---:|---:|---:|
| E5a Zero-shot | 0.273 | 0.818 | 0.409 | 0.421 |
| E5b Few-shot | 0.178 | 0.727 | 0.286 | 0.322 |
| E5c Retrieval | 0.151 | 1.000 | 0.262 | 0.404 |
| E2 on same 80 | 0.350 | 0.636 | 0.452 | 0.599 |
| E4 semantic on same 80 | — | — | — | 0.505 |

**Read carefully:** high recall with low precision is not "better judgement". More historical examples did not stably improve classification on this subset.
**Files:** `judge_classifier_results.csv`.

## E3 · Generation ladder and the feedback-vs-resampling comparison

**What it tests:** does any added component improve generated candidates?
**Optimisation proxy:** frozen E2. **Independent auditor:** E4, which never fed back into generation.
**Result:** O2 − O1 (feedback vs equal-budget resampling) = **+0.0001395**, topic-bootstrap 95% CI **[−0.0008932, +0.0009857]**. Independent E4 audit = **−0.0146241**, CI **[−0.0414844, +0.0074620]**. Both contain zero.
**Two different bootstraps.** The independent audit file recomputed the E2 bootstrap with slightly different interval endpoints. The main comparison table keeps the original endpoints; the two are not merged into one "precise" number.
**Limitation:** no observed exposure, so no real transmission effect can be estimated.
**Files:** `generator_results.csv`, `generator_summary.csv`, `generator_paired_comparisons.csv`, `generator_candidate_results.csv`, `independent_generation_audit_summary.json`, `independent_generation_audit_comparisons.csv`, `independent_generation_candidate_audit.csv`.

## E4 · Supporting checks — and exactly how far they reach

| Check | Result | Limit |
|---|---|---|
| 30 controlled quality cases | 24 invalid / 6 valid, all correctly classified | Narrow pre-designed anomalies only; **not** open-world fact checking |
| Upworthy title transfer | 1,913 experiments; observed CTR order accuracy ≈ **0.510** | Different platform, era and content form; noisy winners |
| Integrity checks | 13 passed | Process constraints only (fixed units, Train-only retrieval, candidate-data correspondence) — **not** content quality |

**Files:** `quality_calibration_cases.json`, `upworthy_transfer_metrics.json`, `integrity_checks.json`, `failure_cases.csv`.

## E5 · Human review — not completed

12 groups were planned, then postponed after the user judged the drafts too abstract to be real posts. **No formal human result exists.** Files under `human_review_package/` are the prepared material and its status record — not a result.

## E6 · Cost and ledger

`cost_summary.json`, `cost_results.csv`, `api_ledger.jsonl`. These are Final generation/evaluation unit allocations, **not** the round's total spend. A 0.244 proxy score must never be translated into a "24.4% virality probability".

---

# Round 2 — Judge admission, Final comparison, and a FAILED protocol audit

## E7 · Judge admission (the ruler is tested before being trusted)

**Design:** 30 controlled comparison pairs — 15 Calibration + 15 Validation — each covering community fit, specificity and information value (5 pairs per dimension), including identical and paragraph-only ties, evaluated with AB/BA swapping.

| Judge | Stage | Agreement | Swap consistency | Community / Specificity / Info value | Verdict |
|---|---|---:|---:|---|---|
| Gemini Lite | Calibration | 12/15 | 86.7% | 5/5, 4/5, 3/5 | Meets threshold |
| Gemini Flash | Calibration | 4/15 | 33.3% | 1/5, 2/5, 1/5 | **Fails** |
| Gemini Lite | Validation | 12/15 | 86.7% | 5/5, 5/5, **2/5** | **Information value below 60% → not admitted** |
| Claude Haiku 4.5 | Validation | 15/15 | 100% | 5/5 each | Passes controlled cases |

**Why this eval exists:** in Round 1 the automatic judge was used to select without ever being validated against its target.
**Critical limitation, stated in the report itself:** these agreements are against **pre-constructed labels by the same person who designed the pairs**, not against human raters. Claude's 15/15 is **not** "100% accuracy at judging community quality". Lite's ~80% overall does not excuse the information-value failure.
**Consequence:** the formal Feedback arm was closed. That is correct protocol behaviour, not a failure of execution.
**Files:** `controlled_pairs_calibration_v002.json`, `controlled_pairs_validation_v002.json`, `challenge_summary_*_v002.json`, `judge_validation_cases/`, `evaluator_admission_v002.json`.

## E8 · Real human naturalness feedback (small, but the most informative human evidence in the project)

One genuine browser submission with 3 Chinese previews: D01 = yes; D03 = no ("information density too high, doesn't look like a real user's post"); S01 = yes ("fairly abstract, hard for me to judge").

**Why it matters:** D03 survived two automatic simplifications and was only fixed by a **manual** edit. That shows concrete editing improves the reader's experience — it does **not** show the automatic chain winning a controlled comparison.
**Limit:** three naturalness *previews*, not three blind pairwise ratings. It must not be rewritten as a "66.7% success rate". The planned 12 human Final groups were never completed.
**Files:** `human_naturalness_submissions/`, `human_naturalness_revision_acceptance_v002.json`, `naturalness_user_review_v002.json`, `naturalness_gate_v002.json`, `naturalness_previews_v002.json`, `naturalness_quality_*`.

## E9 · Round 2 Final comparison

12 new tasks, 108 candidates (V0/V1/V2 = 24 each, O1 = 36).

| Comparison | W | L | Tie | Uncertain | Failure | Decided win rate | Decided coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| V1 vs V0 | 1 | 7 | 0 | 3 | 1 | 12.5% | 8/12 |
| V2 vs V1 | 3 | 2 | 0 | 7 | 0 | 60.0% | 5/12 |
| O1 vs V2 | 0 | 0 | 12 | 0 | 0 | n/a | 0/12 |

Wilson 95% intervals: V1 vs V0 ≈ [2.24%, 47.09%]; V2 vs V1 ≈ [23.07%, 88.24%] — conditional on decidable cases only.

**Two design defects that limit this eval:** (a) V2's 60% rests on only 5 decided comparisons; (b) O1's 12 ties all occur where the selected draft *is* the V2 original, so the arm's treatment intensity was **zero** — it does not test whether extra sampling helps.
**Files:** `final_comparison_results_v002.csv`, `final_comparisons/`, `final_generation_metrics_v002.json`, `final_summary_v002.json`.

## E10 · Protocol and integrity audit — this one FAILS

- Declared token hard cap: **1,000,000**. Audit recorded **1,225,228** → over by 225,228 (**~22.52%**). Runtime did not effectively enforce the cumulative cap.
- **11 per-call manifests and 68 raw responses missing** from early in the run.
- contract/manifest audit of 500 entries: PASS 401, WARN 11, **FAIL 88 → overall FAIL**.
- Final source body reads occurred after freezing; external generator tuning/selection calls = **0** (correct isolation).

**How to use this:** these observations remain valid and are reported **with the protocol deviation attached**. A separate, earlier snapshot of the cost file shows different totals; the report uses the newest ledger and preserves the older file's timestamp rather than calling it false.
**Files:** `final_integrity_audit_v002.json`, `contract_manifest_audit_v002.json`, `cost_summary_v002.json`, `api_ledger_v002.jsonl`.

---

# Round 3 — Dev-stage evaluation and termination

## E11 · Attempt 1 (v003) — the task itself was wrong

| Eval | Result | Limit |
|---|---|---|
| Schema/content inspection of 8 tasks | **All 8 collapsed into a help-seeking frame** | From schema and content inspection — **not** a completed 8-item human preference statistic |
| Independent ownership/identity check | **14/16 passed** | D03's two drafts inherited the source author's first-person experience |
| Claude AB/BA over 8 pairs | **Swap consistency 3/8** | A stability measure, **not** accuracy against humans (no human labels existed) |

**Files:** `EVALS/round3_dev_and_termination/v003/` (`identity_supplement/`, `selector_challenge/`, `translation_readback_clarification_v003.json`, `dev_process_review_v003.json`).

## E12 · JEV — a connectivity probe, not a validation

`typesafe/jev-1.13-20260917` via the native `/api/v1/systemone` endpoint: 389 in / 62 out tokens, **US$0.000016338**, ≈ **0.677 s**, structured narrow judgement with confidence.

**Proven:** the interface was reachable at that moment.
**Not proven:** agreement with human preference, selection of higher-value posts, superiority to Claude, or useful rewrite explanations. **Never completed Dev admission or Final.**

## E13 · Attempt 2 (v004) — archetype redesign, and quality that still blocked release

| Eval | Result | Limit |
|---|---|---|
| Offline dry-run | 27 checks passed | Process constraints only — not generation quality |
| Original automatic quality check | **7/16 passed** | The judge over-blocked attributed/uncertain claims |
| Supplementary publication check | **2/16** met both labels with no listed blocker (both from E01) | Covers only some risks |
| Independent identity/fact audit | Run, retained | Not a guarantee of correctness |
| Process audit status | `PASS_WITH_DOCUMENTED_BRIEF_REPAIR` | **Not** zero-deviation; **not** fully automatic |
| Formal 8-group human preference | **Not completed** | Must not be reconstructed |
| JEV / alternative selector admission | **Not completed** | — |
| Title module human validation (4) | **Not run** | — |
| Product freeze P* then 6 Final tasks | **Not run** | — |

**Failure classes found:** internal fact numbering leaking into bodies (the rule missed lowercase `f`); 2025 material described as "recently" without a date; a specific tutorial generalised to an entire technology category; one over-confident restatement of a source's criticism; judge disagreement on whether attributed/uncertain claims were `unverified`; and a residual third-party **summary tone** even where the help-seeking collapse was fixed.

**Two numbers that must not be misread.** **7/16 and 2/16 are process labels — not content accuracy, hallucination rates, or real publishability.** The remaining 14 drafts must not be called "14 pieces of false content". Faithful translation did not rewrite the problems away; a numeric-format change is not a translation error.

## E14 · Termination note

At termination the new Dev interface was ready but **no formal complete human evaluation submission exists**. The user stopped the round on the basis of observed content quality. The required framing is:

> **Round 3 terminated early at the Dev stage due to poor real-human quality feedback. No valid conclusion about G1 versus G0 can be given.**

This is neither a success dressed up, nor missing data silently converted into a failure win-rate.

---

# What each eval ultimately established — and did not

**Established**
1. On this cleaned 2025 r/LocalLLaMA data with temporal splits, a text model discriminates historical relative high score better than a constant ranking.
2. Round 1's RAG, pattern cards and feedback loops did not consistently improve the generation proxy or the independent audit. Complexity is not self-justifying.
3. An internal judge with a good overall agreement rate can still fail on a specific dimension. Admission must be per-dimension and coverage-aware.
4. Round 2's full-input V0 was preferred over this particular compressed V1 in a small external comparison.
5. Real human feedback surfaced unnaturalness, over-density and abstraction that automatic scores did not reflect.
6. A uniform "current decision + help me" schema changes tasks that were originally different types.
7. Automatic judges disagree with each other on attributed and uncertain claims; the favourable label cannot be cherry-picked.
8. Added complexity did not stably improve transmission value; a simple, complete, fact-constrained default is the more defensible route.

**Not established**
- That ViralLoop is a validated, automatically acceptable viral copy generator.
- That E2/E4 scores on generated text are real high-performance probabilities.
- That titles, length, conflict framing or any specific pattern caused real engagement gains.
- That RAG, Feedback, Motivation or the Engagement Planner are universally useless.
- That V0 is universally better than all strong prompts, all RAG, or all advanced models.
- That Claude or JEV accurately represent community users, or that a connection or controlled calibration validates product capability.
- That passing 30 controlled cases proves open-world factual safety.
- That Round 3 completed human admission, title trials, or Final.
- That a low API bill equals low R&D cost or demonstrated commercial ROI.
