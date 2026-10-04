# DATA_README — Data Provenance, Cleaning and Splits

This folder contains **only the data files that were actually used** and that are needed to reproduce or audit the report's numbers. Large regenerable corpora are deliberately excluded (see §6).

---

## 1. Source

| Item | Value |
|---|---|
| Dataset | [`pszemraj/LocalLLaMA-posts`](https://huggingface.co/datasets/pszemraj/LocalLLaMA-posts) |
| Community | Reddit **r/LocalLLaMA** — local LLMs, models, hardware, inference tooling |
| Raw rows | **100,679** |
| Licence | ODC-BY (dataset). Reddit author text may carry separate rights — see §7 |
| Target signal | `score` — a net vote value from the archive |

**Why this dataset.** Alternatives were assessed and rejected: Product Hunt taglines are too short for full-post generation; Xiaohongshu mixes image and text contribution; Medium claps are not unique readers and its recent corpus is narrow. r/LocalLLaMA offers real text with real historical feedback, and constrains the domain so platform and topic are held roughly constant.

**What `score` is not.** It is not impressions, exposure, clicks, or unique likes. The project target is therefore **relative high score within the same community and time window** — not "viral".

## 2. Pipeline — raw to model-ready

| Stage | N | Meaning |
|---|---:|---|
| Raw corpus | 100,679 | Public archive |
| Free-rule candidates | 20,019 | 2025 only; text-only; type/length filters |
| Stratified recovery | 2,800 | Sampled by month × rule-type — **never sampled by score** |
| Observation audit | 400 | Probes used to verify the time window |
| **Final model data** | **2,336** | After age-window filtering and a second clean |

Filtering excluded cross-year posts, missing bodies, image/media posts, unsuitable lengths, obvious news releases, duplicates and pinned posts.

**Known weakness, stated honestly.** Automated content-type rules cannot guarantee semantic accuracy. In Round 3 it was still found that model releases and product showcases had been mislabelled as experience or discussion posts. The type label is an *approximation*, and the report treats it as such.

Files: `filter_summary.json`, `cleaning_log.csv`, `content_types.csv`, `duplicate_groups.csv`.

## 3. The 36–38 hour observation window

The raw fields did not guarantee that every post had accumulated engagement over the same amount of time. Without correcting this, an older post would look better simply because it had been visible longer.

**What was done.** `score` and `retrieved_on` were recovered from the same upstream archive (Arctic Shift), retaining responses, audits and request timestamps. Across a **400-post probe, 95.75%** of posts were observed at approximately **36–38 hours** of age. That window was fixed, and filtering then proceeded within it.

**What this solves:** it removes part of the difference in accumulation time.
**What it does not solve:** exposure, platform recommendation, news intensity, or competing posts. The observation *age* is roughly equal; the observation *opportunity* is not. Tagging and body text may also differ slightly from the moment of publication (initial archive typically ~17 s after posting).

Files: `observation_window_analysis.csv`, `recovery_audit.csv`, `recovery_decision.json`, `raw_audit.csv`.

## 4. Label definition

> **Positive** = a post whose `score` is **strictly above the 75th percentile** of its `month × content-type` group. Groups with fewer than 20 posts fall back to the month level. Ties are **not** forced positive, so the positive rate is not exactly 25%.

Building the label from post-publication outcome is normal supervised learning. **Feeding a post-publication field into the model is leakage** — this is prohibited throughout the project (§5).

## 5. Splits and leakage control

| Split | Months | N | High-performing | Used for |
|---|---|---:|---:|---|
| Train | Jan–Jul | 1,396 | 337 | Training, retrieval, pattern discovery |
| Tune | Aug–Sep | 398 | 99 | Tuning, thresholds, development decisions |
| Selection | Oct | 194 | 49 | Model selection, freezing |
| **Final** | **Nov–Dec** | **348** | **86** | **Held-out historical evaluation only** |

Splits are **temporal**, so the model never trains on the future relative to its test set.

**Leakage controls applied:**
- No post-publication field (`score`, comments, any derived outcome) ever enters the feature set.
- Thresholds come from development data and are frozen before Final — never re-picked on Final.
- Retrieval (RAG) draws from **Train only**; Final cases never enter the retrieval library.
- Author history uses only posts already observed *before* the target post's publication, and missing history is encoded as missing rather than imputed.
- Generation sources are isolated by issue / benchmark / near-duplicate, with no source crossing partitions.

Author-clustered bootstrap is used for intervals, which partially accounts for dependence between posts by the same author.

## 6. What was used in each round

| Round | Data actually used |
|---|---|
| **Round 1** | Full 2,336 frozen dataset; Final 348 for historical evaluation; Train-only retrieval for RAG; 10 experimental generation briefs (a separate evaluation set — **not** the 348 historical posts) |
| **Round 2** | Reused the same 2,336 posts, E2/E4, Train retrieval and cache. **No retraining.** 18 new generation tasks (4 Tune, 2 Selection, 12 Final). Sources S01/S02 demoted to development after early preview |
| **Round 3** | Reused the same data. New sources drawn from Train by fixed hash/rule, excluding earlier-round sources and near-duplicates. 8 Dev tasks in Attempt 1 (v003) and 8 in Attempt 2 (v004). Final sources were never frozen |

## 7. Raw vs processed vs experimental subsets

- **Raw** (`data/raw/`, 65 MB) — excluded from this package. Regenerable from the documented download script.
- **Processed** — `processed_posts.parquet`, `recovered_posts.parquet`, `labels.parquet`, `splits/*.parquet`. **Included.**
- **Experimental subsets** — briefs, sources, and Dev/Final task assignments. **Included** under `round2_briefs_and_sources` and `round3_briefs_and_sources`.

**Excluded from the package (size and/or regenerability):** `raw/` (65 MB), `embeddings/` (108 MB), `candidate_pool.parquet` (19 MB), `recovery_cache/` (16 MB), `vendor/` and `vendor_runtime/` (bundled third-party libraries), and per-call API caches. These are regenerable with the scripts in `CODE/`.

## 8. Rights and re-distribution

The dataset itself is **ODC-BY**, but the underlying Reddit author text may carry independent rights. Publicly downloadable does **not** mean licensed for commercial redistribution. The original archive also contains author fields, which are unsuitable for direct use as public product logs.

**Accordingly:** this repository ships processed artefacts and documentation rather than a commercial redistribution of author text. Any course reproduction or data re-distribution should keep the existing data statement, and where necessary substitute the download script, the documentation, and samples that are cleared for publication. A full commercial-licence review was **not** completed.
