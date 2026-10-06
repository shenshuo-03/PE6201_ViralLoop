# Data notes

Primary source: [pszemraj/LocalLLaMA-posts](https://huggingface.co/datasets/pszemraj/LocalLLaMA-posts). The dataset card marks it ODC-BY and the original archive comes from Arctic Shift. `raw/DATASET_CARD.md` and the original Parquet files are retained. The underlying Reddit author text may still carry separate rights; reproducing it for a local course experiment is not a grant of commercial redistribution rights.

100,679 raw records → 20,019 candidates passing the free rules → 2,800 recovered by stratified random sampling across 2025 months × rule-based types → 400 audited → 2,336 after the 36–38h observation window and a second cleaning pass. Split months and labelling rules are set out in the execution contract. Do not filter samples by score.

- `raw_audit.json/csv` — complete local data statistics.
- `cleaning_log.csv` — keep/drop decision and reason for every row. This is not "cleaning by popularity".
- `candidate_pool.parquet` — posts left by the free rules.
- `recovery_cache/` — full upstream responses and request times. May contain original public fields such as author, and is not exposed in public product logs.
- `recovery_audit.csv` / `recovery_decision.json` — evidence behind the 400 recovery decisions and the window choice.
- `recovered_posts.parquet` — score and observation time come from the same source record.
- `processed_posts.parquet` — final model input and outcome, with partition assignment.
- `labels.parquet` — retrospective month × type Top-25% label, strictly greater than the threshold. Ties are not forced into the positive class.
- `splits/` — chronological partitions.
- `embeddings/` — cached output of a real semantic model; text input only, truncated at 4,000 characters.

First collection usually happened about 17 seconds after publication, but a minority of records are later, so the archived "content before publication" is only an approximation. Author history covers only posts already fully observed within this sample; it is not a complete reputation measure.

The object of study is conditional historical performance. Exposure, platform recommendation, news intensity and complete author reputation are all missing, so no causal interpretation is made. Nothing is posted automatically without authorisation, and source posts are never treated as instructions.
