# Round 2 Explainer — Real Material, an Independent Judge, and a Ruler That Failed Admission

Round 2 workspace (`loops/v002`) → packaged as `CODE/round2_v002`, `DATA/round2_briefs_and_sources`, `EVALS/round2_judge_and_final`.

## What Round 2 changed

Round 1's weakness was that the task itself was not real: synthetic briefs, no genuine reason to post. Round 2 fixed the input and tightened the evaluation:

- **Input:** real source material with a full brief (purpose, audience, facts, dates, identity, forbidden claims).
- **Evaluation:** an automatic judge must **pass admission** before it is allowed to select anything.
- **Isolation:** an external Claude Final judge was excluded from all tuning and selection — audit recorded **0** such calls. This removes the "tune on a judge, then use the same judge to prove the product works" loop.
- **Reuse:** the 2,336-post dataset, E2/E4, Train retrieval and cache were reused; no retraining.

18 tasks were scheduled: 4 Tune, 2 Selection, 12 Final. Sources were isolated by issue/benchmark/near-duplicate, with no source crossing partitions.

> **Disclosed partition change.** Sources S01/S02 were originally Selection but were previewed early, so they were demoted to development material and replaced by S03/S04. The old S01/S02 must not be described as unseen selection items.

## Version definitions, and where they deviate

| Version | What it actually does | Known deviation |
|---|---|---|
| **V0** | Full brief, simple generation instruction, identity/date/fact requirements; 2 drafts per task | A *full-input baseline with safety constraints* — not a bare LLM |
| **V1** | Focus on one purpose and 1–2 facts; shorter body, fewer questions | **Deletes context, motivation, desired_response, missing_information and allowed_claims** from the input |
| **V2** | V1 route plus structure-oriented RAG | Inherits V1's input change — its result cannot be attributed to RAG alone |
| **O1** | 3 extra drafts on top of a V2 draft, original retainable | Selector not admitted → eligible-order fallback; all 12 Final tasks kept the original |
| **O2 / V3 Feedback** | Planned diagnose-then-rewrite against O1 | **Closed** — admission conditions not met, no formal Final result |

**This is the single most important caveat in Round 2.** V1 is not "strong prompt added" — it simultaneously **reduces input information and changes the length target**. So the correct conclusion is *"this focus/compression approach did not beat the full-fact baseline"*, **not** *"a strong prompt is worse than a simple one"*.

Generation params: V0 ≈ temp 0.5, output cap 1,800 tokens, target body 90–230 words. V1 ≈ temp 0.2, cap 450 tokens, target 90–150 words. O1 additionally capped near 2,700 tokens.

Structure-oriented RAG used TF-IDF (1–2 gram, min_df=2, max_features=15,000, sublinear TF): 2 high-performing and 1 ordinary example per type, from which only a **structure summary** was extracted — deliberately avoiding injecting historical names, numbers and facts into the current brief.

## Judge admission — the ruler was tested, and it failed

30 controlled comparison pairs (15 Calibration, 15 Validation), each covering community fit, specificity and information value, including exact ties and paragraph-only changes, with AB/BA swapping.

| Judge | Stage | Overall agreement | Swap consistency | Community / Specificity / Info value | Verdict |
|---|---|---:|---:|---|---|
| Gemini Lite | Calibration | 12/15 | 86.7% | 5/5, 4/5, 3/5 | Meets threshold at this stage |
| Gemini Flash | Calibration | 4/15 | 33.3% | 1/5, 2/5, 1/5 | **Fails** |
| Gemini Lite | Validation | 12/15 | 86.7% | 5/5, 5/5, **2/5** | **Information value below the 60% threshold → not admitted** |
| Claude Haiku 4.5 (external) | Validation | 15/15 | 100% | 5/5 each | Passes controlled cases |

**Two readings that must be kept straight:**

1. These agreements are against **pre-constructed comparison labels**, not against 30 human raters. Claude's 15/15 is *not* "100% accuracy at judging community quality" — it means it agreed with pairs designed by the same person who designed the test.
2. Lite's overall ~80% must not hide the **information-value dimension failure**. A judge can be broadly agreeable and still be specifically blind on the dimension that matters.

Closing the formal Feedback arm was therefore the correct decision under the protocol. Internal quality scores, when still used for gating, are an **engineering tool** — not calibrated evidence.

## Real human naturalness feedback — small, but decisive

One genuine browser submission recorded 3 Chinese previews:

| Preview | Choice | Raw note |
|---|---|---|
| D01 | yes | (none) |
| D03 | no | "Information density is too high — doesn't look like something a real user would post" |
| S01 | yes | "Fairly abstract, technically difficult — hard for me to judge" |

D03 remained too dense after **two** automatic simplifications. A **manually edited** revision then received a "yes". That shows concrete editing improves the reader's experience — it does **not** show the automatic chain winning a controlled comparison.

These three previews are not three blind pairwise ratings and must not be reported as a "66.7% success rate". The planned 12 human Final groups were never completed.

## Selection and Final

On only two Selection tasks, the pre-set simplification rule kept **V0**. That is not proof that V0 is best across many real user tasks.

Final comprised 12 new tasks adding **108 candidates**: V0/V1/V2 at 24 each, O1 at 36.

| Version | New candidates | Hard checks passed | Selected coverage | Mean body words |
|---|---:|---:|---:|---:|
| V0 | 24 | 22/24 | 12/12 | 143.7 |
| V1 | 24 | 24/24 | 12/12 | 110.5 |
| V2 | 24 | 24/24 | 12/12 | 117.6 |
| O1 | 36 | 36/36 | 12/12 | 115.8 |

Hard checks permitted 70–300 words — *wider* than the prompt's target. "Hard passed" therefore does **not** mean "met the writing target".

External judge Final results:

| Comparison (first listed wins) | W | L | Tie | Uncertain | Failure | Decided win rate | Decided coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| V1 vs V0 | 1 | 7 | 0 | 3 | 1 | 1/8 = 12.5% | 8/12 = 66.7% |
| V2 vs V1 | 3 | 2 | 0 | 7 | 0 | 3/5 = 60.0% | 5/12 = 41.7% |
| O1 vs V2 | 0 | 0 | 12 | 0 | 0 | n/a | 0/12 |

Conditional win rates carry Wilson 95% intervals of roughly **[2.24%, 47.09%]** for V1 vs V0 and **[23.07%, 88.24%]** for V2 vs V1 — these apply only to decidable cases, not to all tasks.

**Two caveats that matter more than the point estimates:**

- V2's 60% rests on **only 5 decided comparisons**, with 7 uncertain. That is very weak evidence.
- O1's 12 Ties are all cases where the selected draft *is* the V2 original. The judge never faced a real choice, so this is **not** evidence that "extra sampling is useless" — it means the fallback removed the treatment entirely.

## Engineering and protocol findings

Reported together because they belong together:

- Round 1 data and ledger snapshots unchanged; frozen-code checks passed.
- Final source body reads occurred after freezing; external generator tuning/selection calls = **0**.
- No formal Feedback calls were made after admission failed.
- **But:** 11 per-call manifests and 68 raw responses were **missing** early in the run. These cannot be back-filled or rewritten as if they had been saved.
- Declared token hard cap **1,000,000**; audit recorded **1,225,228** — over by 225,228 (~22.52%). The cumulative cap was **not effectively enforced at runtime**.
- contract/manifest audit of 500 entries: PASS 401, WARN 11, **FAIL 88 — overall FAIL**.

## Decision carried into Round 3

Do not extend RAG or Feedback. Test only real motivation, lightweight planning and a selector, and align the evaluation target with **real human Dev feedback** first.
