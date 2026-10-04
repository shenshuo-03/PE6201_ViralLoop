# PRODUCT_DOCUMENTATION — ViralLoop

Required sections: Persona · Problem · Input · Output · original architecture · final simplified architecture · external intelligence used · metrics targeted · metrics actually reached · cost · known limitations · final product decision.

---

## 1. Persona

**Wei**, 26, an engineer at an early-stage AI startup in Singapore.

He has just finished an internal benchmark on local inference and found something genuinely surprising — a configuration that cut p99 latency far more than expected. He has 40 minutes between meetings, a scratch file of raw numbers, and a VS Code window still open on the test harness.

He reads r/LocalLLaMA and Hacker News every day. He has **never posted on either**. What stops him is not laziness: he genuinely does not know whether "we cut p99 from 480 ms to 90 ms" is the headline or a footnote, whether the caveat about his test setup kills the post, or whether this is interesting to anyone but him.

He does **not** know what a scoring model is, and would not trust one if he did. He would, however, read a draft that sounded like *him*, better organised.

**What changes when the system works:** Wei gets a draft he recognises as his own point — and posts it in ten minutes instead of abandoning it.

## 2. Problem

People in technical fields have things worth sharing, but the judgement about *what the hook is* and *what to leave out* is tacit and hard-won.

Existing tools (ChatGPT, Jasper, Copy.ai, community drafting helpers) optimise for fluency and completeness. The failure mode is distinctive and dangerous: a confident, well-written, well-organised post that no community member would ever write or read — with no signal to the author that this is what happened.

## 3. Input

| Field | Meaning |
|---|---|
`posting_intent` | Why the author actually wants to post today (not "generate a post about X") |
`speaker_role` | Who the author is relative to the material: own work / project participant / third party |
`content_archetype` | finding · opinion · resource · question · comparison · tutorial · retrospective |
`source_relationship` | How the author relates to the material |
`facts` | The verifiable facts, with dates |
`forbidden_claims` | What the author must not claim |
`audience` / `language` / `length_target` | Delivery constraints |

## 4. Output

| Field | Meaning |
|---|---|
| Draft | Title + body, in the author's voice |
| Source correspondence | Which facts came from where |
| Risk flags | Fact, identity, date and scope issues found by deterministic rules |
| Version and cost record | For auditability |
| Insufficient-material report | The system declines rather than inventing a hook |

The system **never** outputs: a virality probability, a guaranteed engagement lift, or an auto-published post.

## 5. Original product architecture (as designed)

```
Historical posts + outcomes
        ↓
Cleaning & observation-time recovery
        ↓
Historical prediction model ──┐
        ↓                     │
Train retrieval + pattern cards
        ↓                     │
User topic + material → LLM candidate generation
        ↓
Fact / quality gate ←─────────┘
        ↓
Draft selection
        ↓
Feedback or one-step rewrite → back to the gate
        ↓
Independent audit + human check
```

This diagram shows **candidate components across all rounds — it is not a single pipeline that ever ran end to end**. Round 1 ran the feedback comparison; Round 2 closed formal feedback after admission failure; Round 3 never reached feedback, titles or Final.

## 6. Final simplified architecture (the actual recommendation)

```
Real author intent + dated material
        ↓
Complete fact brief
        ↓
Simple fact-constrained LLM drafting
        ↓
Deterministic rule + source checks
        ↓
Human confirmation and edit
        ↓
Usable draft
        ↓ (side channel, always on)
Record inputs, outputs, cost and problems
```

Historical prediction and RAG remain as **research tools**, not required product components. Checks block or warn; they do not replace human responsibility. There is no automatic publish path.

## 7. External intelligence used

| Component | What is used | Evidence status |
|---|---|---|
| Generation | `openai/gpt-4.1-mini` (Rounds 2–3), `google/gemini-2.5-flash-lite` (Round 1) | Real runs, ledger-recorded |
| Internal quality judge | `google/gemini-2.5-flash-lite`, `google/gemini-2.5-flash` | Lite **failed admission** on information value; Flash failed outright |
| External Final judge | `anthropic/claude-haiku-4.5` | Passed controlled cases; excluded from tuning and selection (0 calls) |
| Alternative judge | `typesafe/jev-1.13-20260917` via native `/api/v1/systemone` | **One connectivity probe only** — never admitted, never used for Final |
| Embeddings | `openai/text-embedding-3-small`, truncated at 4,000 chars | Used for E4 |
| Narrow ML | TF-IDF + logistic regression (E2), LSA (E4) | **Own build**; the only layer with real held-out support |
| Retrieval | TF-IDF over Train only | Own build |
| Translation | LLM translation of blind cases into Chinese | Reviewer accessibility; did not alter the English source |

**Build vs buy:** own the data processing, splits, labels, narrow classifiers, retrieval, orchestration, cache, ledger, and human interface. Rent embeddings and generation. Never delegate the final selection or the publish decision.

## 8. Metrics targeted

| Metric | Target | Baseline to beat |
|---|---|---|
| Historical **Average Precision** on the 348-post Final split | ≥ 0.40 | Lazy baseline **0.247** |
| Judge admission agreement per dimension | ≥ 60% per dimension | — |
| Human relative preference (generated vs baseline) | Positive | Equal-budget resampling |
| Abstention behaviour | Reported and characterised | — |

AP was chosen over accuracy because the positive class is a ~24.7% minority — a system that never predicts the positive class scores 0.753 accuracy and is worthless. That is precisely the trap the course watch-out names.

## 9. Metrics actually reached

| Metric | Reached | Honest reading |
|---|---|---|
| Historical AP | **0.552 (E2) / 0.585 (E4)** on 348 posts | **The one clear success.** E2's AP increment over the prior: bootstrap CI ≈ [0.219, 0.405] |
| Generation proxy gain from complexity | **+0.0001395** (O2−O1), CI contains 0 | No stable gain |
| Independent audit of the same comparison | **−0.0146**, CI contains 0 | Confirms no gain |
| Judge admission | Lite **failed** information value (2/5) | The ruler failed its own test |
| Round 2 external Final | V0 preferred over V1 in 8 decided cases; V2 vs V1 60% on only 5 cases | Small-sample automatic result only |
| Round 3 human Dev result | **Not completed** | Terminated early |
| Online engagement | **Never measured** | Cannot be claimed |

**A proxy score of 0.244 is not a 24.4% virality probability.** A 1-in-8 win rate is not a 12.5% product success rate.

## 10. Cost

| Round | Ledger entries | Tokens | API cost (US$) |
|---|---:|---:|---:|
| Round 1 | 350 | 1,403,922 | 0.344225350 |
| Round 2 (v002) | 500 | 1,230,780 | 0.708652800 |
| Round 3 Attempt 1 (v003) | 82 | 236,381 | 0.166365038 |
| Round 3 Attempt 2 (v004) | 64 | 179,207 | 0.097554900 |
| **Total** | **996** | **3,050,290** | **1.316798088** |

Budget ceiling: US$5. Recorded spend is within it.

**This is not the production cost per use.** It is R&D spend including development, checks, retries and probes. It excludes Codex reasoning, human time, local compute and storage.

**The cost that actually constrained the project was not money.** It was: reconciling versions and confounds, checking source identity, repairing briefs by hand, resolving model JSON/rule conflicts, preserving complete archives, and getting a human to judge highly technical content in a second language. Complexity cost is not only extra cents per draft — it is extra disagreement, extra failure points, and extra judgement burden on the user.

## 11. Known limitations

| Category | Actual problem | Effect on conclusions |
|---|---|---|
| Data | No exposure, news intensity, or author reputation observed; text may have been edited | Vocabulary association cannot be read as a causal effect of wording |
| Labels | Relative score within month × type; rule-based type classification has errors | Not a universal "viral" definition |
| Time | Fixed observation age ≠ fixed recommendation opportunity | Only part of the confounding is controlled |
| Round 1 task | Hypothetical briefs; abstract drafts | Generated posts may not match real use |
| Round 1 human | 12 groups postponed | No overall human comparison |
| Round 2 versions | V1 deleted context while changing length | Cannot be attributed to prompt technique |
| Round 2 judge | Controlled calibration ≠ human preference | Automatic quality score is not product acceptance |
| Round 2 O1 | Fallback returned the original (12 ties) | Never tested selection increment |
| Round 2 engineering | Token cap exceeded; 11 manifests / 68 responses missing | **Protocol audit FAIL** |
| Round 3 Attempt 1 | All types forced into help-seeking | The task itself was altered |
| Round 3 Attempt 2 | Sampling rules revised; assistant repaired briefs | Not fully automatic, not zero-deviation |
| Round 3 audit | Over-blocking; missed lowercase numbering; scope generalisation | Pass rate ≠ factual accuracy |
| Human | Single reviewer, translated into Chinese, different technical background | Not representative of the target community |
| Statistics | Small topic counts; low decided coverage; many exploratory arms | Wide intervals; no general ranking |
| Statistics (power) | No minimum detectable effect was computed; 10–12 topics cannot detect the effects being targeted | **The experiment was underpowered by construction** |
| Online | Never published | No real engagement evidence exists |
| Rights | ODC-BY dataset, but underlying author text may carry separate rights | No commercial redistribution |

## 12. Final product decision

**Retain:** complete fact brief · simple fact-constrained LLM drafting · deterministic checks · mandatory human confirmation · full ledger and provenance.

**Retain as research assets, not product components:** historical prediction (E2/E4) · RAG · pattern cards.

**Close:** the feedback loop as a default path · multi-sample with selector · motivation/engagement planner · title optimiser.

**Not claimed:** that this generates viral posts, that the loop improves outcomes, or that any part of it has been validated online.

> **ViralLoop is a research prototype for fact-constrained community content drafting and evaluation. It organises dated, sourced material into a fact-constrained draft and studies the limits of content optimisation through a historical model, automatic checks and real user feedback. Existing experiments have not established a real transmission improvement; the current defensible route is complete input, simple generation, explicit checks and human confirmation.**

The name may be retained, but "Viral" must not be read as a proven promise. The emphasis shown to users should be *"help me express something real"*, not a virality percentage that was never calibrated online.

**Why this is a decision and not a surrender.** The three rounds did not fail to build the loop — they built it and measured it. What they found was that the bottleneck moved away from the machinery and towards three things no amount of extra components could fix: whether the task is real, whether the ruler is calibrated, and whether the added complexity is worth its cost.
