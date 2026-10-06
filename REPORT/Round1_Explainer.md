# Round 1 Explainer — Historical Signal Is Real, Generation Gain Is Not

Round 1 workspace → packaged as `CODE/round1_generation_pipeline`, `DATA/round1_dataset`, `EVALS/round1_historical_and_generator`.

## What Round 1 asked

Two questions, deliberately separated:

1. **Can historical high performance be learned?** → evaluated on real old posts.
2. **Does that learning improve generated posts?** → evaluated on generated candidates.

Keeping these separate matters, because they are different estimation problems. A predictor answering *"is this text in the historical top quartile?"* is not answering *"if I rewrite this, will it score higher?"*

## Setup

- Data frozen first: 2,336 posts, temporal splits (Train 1,396 / Tune 398 / Selection 194 / **Final 348**).
- Historical evaluator ladder E0–E4 frozen before any generation.
- Generator used **Gemini 2.5 Flash Lite**; independent quality evaluation used **GPT-4.1-mini**.
- E2 served as the optimisation proxy; **E4 was an independent auditor that never fed back into generation**.

## Historical evaluator ladder (Final, 348 posts, positive rate 0.247)

| Model | Precision | Recall | F1 | AP | ROC-AUC | Brier | Accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| E0 lazy (always negative) | 0.000 | 0.000 | 0.000 | 0.247 | 0.500 | 0.247 | 0.753 |
| E0 constant prior | 0.000 | 0.000 | 0.000 | 0.247 | 0.500 | 0.186 | 0.753 |
| E1 context only | 0.291 | 0.500 | 0.368 | 0.305 | 0.566 | 0.185 | 0.575 |
| E1b context + structure | 0.381 | 0.593 | 0.464 | 0.420 | 0.711 | 0.170 | 0.661 |
| E2 TF-IDF + logistic regression | 0.510 | 0.605 | 0.553 | 0.552 | 0.765 | 0.180 | 0.759 |
| E3 text + context | 0.468 | 0.686 | 0.557 | 0.500 | 0.775 | 0.160 | 0.730 |
| E4 LSA | 0.392 | 0.674 | 0.496 | 0.540 | 0.758 | 0.154 | 0.661 |
| E4 semantic embedding | 0.451 | 0.698 | 0.548 | 0.585 | 0.789 | 0.148 | 0.716 |

**Reading it correctly.** The lazy baseline's 0.753 accuracy is exactly the trap the course warns about — it is 0.753 by never predicting the positive class. AP is the metric that exposes this. Author-clustered bootstrap put E2's AP increment over the prior at approximately **[0.219, 0.405]**, so the historical signal is genuine.

E4 semantic used `openai/text-embedding-3-small`, truncated at 4,000 characters. Thresholds came from development data and were frozen before Final — they were not re-picked on the test set. `evaluator_results.csv` and `evaluator_dev_results.csv` hold the numbers; `evaluator_bootstrap.json` holds the intervals.

## Generation ladder — 180 candidates, 8 arms

| Arm | Design | Hypothesis tested |
|---|---|---|
| G0 Generic | Minimal instruction, fixed brief | Floor reference |
| G1 Prompt | Explicit writing, fact and structure requirements | Does prompt engineering help? |
| G2 Few-shot / Planning | Examples + planning step | Does demonstration help? |
| G3 RAG | Retrieve related historical cases from Train | Do historical examples help? |
| G4 Positive | RAG + positive pattern cards | Do high-performance patterns help? |
| G4 Both | Positive + negative pattern cards | Does fuller experience help? |
| O1 Resample | 3 extra drafts from the same seed, original retainable | Equal-budget search baseline |
| O2 Feedback | 3 rewrites with predictor/pattern feedback, original retainable | Does feedback beat extra sampling? |

Retrieval used **Train only** — Final cases never entered RAG. Candidates passed a quality gate, then a frozen E2 selected. Final produced 180 candidate records; the independent audit recorded **178 unique texts**, and duplicate cache entries are deliberately not counted as extra independent samples.

## Result

| Version | Mean E2 proxy | Auto quality | Clickbait score |
|---|---:|---:|---:|
| G0 | 0.243551 | 4.100 | 1.000 |
| G1 | 0.241535 | 4.150 | 1.000 |
| G2 | 0.241521 | 4.050 | 1.000 |
| G3 | 0.241345 | 4.075 | 1.000 |
| G4 Positive | 0.242448 | 4.050 | 1.000 |
| G4 Both | 0.240208 | 4.000 | 1.000 |
| O1 | 0.241574 | 4.100 | 1.000 |
| O2 | 0.241713 | 4.050 | 1.000 |

**The headline comparison** — feedback versus equal-budget resampling:

- E2 difference **O2 − O1 = +0.0001395**
- Topic bootstrap 95% interval **[−0.0008932, +0.0009857]** → contains zero
- Independent E4 audit difference **−0.0146241**, interval **[−0.0414844, +0.0074620]** → contains zero

G4 Both scored *below* G0, and E4's interval covered zero. The defensible statement is: **this combination of complex modules produced no consistent offline positive evidence.** It is *not* evidence that RAG reduces real engagement.

**A 0.244 proxy score is not a 24.4% virality probability.** It is a score from a model trained on a distribution different from that of generated text.

## Supporting checks and their limits

- **30 controlled quality cases** (24 invalid, 6 valid): all correctly classified on the pre-specified narrow anomaly types. This does **not** generalise to open-world fact checking.
- **Upworthy title transfer**: 1,913 experiments; observed CTR order accuracy ≈ **0.510**, essentially chance. Platform, era and content form all differ, so it does not validate Reddit full-text behaviour.
- **13 integrity checks passed** (fixed task units, Train-only retrieval, candidate-data correspondence). These support *process* constraints, not content quality.

## The turn

Automatic quality scores were uniformly high and nearly indistinguishable across arms. **Human reaction was the opposite:** reviewers found the drafts too abstract and unlike real community posts. The planned 12 human groups were postponed and never completed.

That divergence is the most important output of Round 1: **the automatic ruler rewarded clarity, completeness and compliance; the humans were asking whether anyone would post it.** The proxy and the humans were optimising different things.

## Decision carried into Round 2

Use stronger, real source material with a full brief; check naturalness first; require the automatic judge to pass admission; keep the external Final judge out of tuning and selection.
