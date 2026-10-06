# RAW_EVIDENCE_NOTE — the 176 files that still contain Chinese, and why

The submission package is English. **Three deliberate exceptions are documented here so a marker is not surprised by them, and so the reason for each is on the record.** Together they are 176 of the 5,507 files in this repository — plus this note itself, which quotes the Chinese it is describing.

Reproduce the count yourself:

```bash
python CODE/scan_cjk.py            # lists every file, worst first
python CODE/scan_cjk.py --summary  # counts per documented category only
```

---

## A · The raw per-call API record layer — 166 files

```
EVALS/round1_historical_and_generator/api_cache/      24
EVALS/round2_judge_and_final/api_cache/               38
EVALS/round2_judge_and_final/runs/                    37
EVALS/round3_dev_and_termination/v003/{runs,api_cache}  43  (v003)
EVALS/round3_dev_and_termination/v004/{runs,api_cache}  24  (v004)
```

These are the verbatim request, response and manifest records the experiment runner wrote at the moment each API call was made.

### Why they are not translated

The pipeline was designed as follows: generate in English, then make one further call to produce a faithful Chinese rendering of the finished task and drafts, so the human reviewer (the author, a Chinese speaker) could read them quickly. A large share of the Chinese in these files is the output of exactly that step — for example a record whose manifest carries `"tag": "translate:D03"` and whose prompt reads *"Faithfully translate task goal, decision, desired help and two supplied drafts into simplified Chinese."*

There are only two ways to remove that Chinese:

1. **Rewrite the records in English.** That would replace a verbatim provider response with text the provider never returned. A frozen call log is meaningful precisely because it is byte-for-byte what happened. Rewriting it would be fabrication, and it would also break the hash baselines other checks verify against.
2. **Delete the records.** That would destroy the strongest evidence that the experiments were really executed, remove the per-call cost trail behind every figure in the report, and break the v003 preservation baseline (`attempt1_preservation_baseline_v004.json`), which covers these files by SHA-256.

Neither is acceptable on a project whose rubric includes honesty about evidence. **Leaving the frozen call record untouched is the only option that does not falsify something.**

Note that this layer is *additive*: the caches and run records are shipped so that Round 1's final test can be re-derived at zero cost (`CODE/run_all_checks.py` proves it reproduces bit-for-bit).

## B · Verbatim dataset text — 1 file

`DATA/round1_dataset/recovery_audit.csv` contains six Chinese characters inside the **verbatim text of the original Reddit posts** (for example an author writing "the first整理 (organization)", and one filename containing non-Latin characters). That is the research object, not documentation; translating it would corrupt the dataset.

## C · Preserved originals of the frozen round code — 9 files

`CODE/_frozen_code/round2_v002/` and `CODE/_frozen_code/round3_v004/` hold **byte-identical copies of the original modules** whose SHA-256 the round freezes record. Their Chinese is the point: they exist so a reader can verify that the code which produced the evidence is unchanged, and can diff it against the packaged copy. `CODE/REPRODUCTION.md` §3 explains the mechanism; `CODE/verify_packaged_code.py` enforces it.

---

## What this does and does not mean

- It does **not** mean the submission is partly in Chinese. Nothing a marker reads in order to understand the project — report, problem statement, explainers, READMEs, module guide, code comments and prompts, configuration, data descriptions, product documentation, web interfaces, CSV and JSON summaries — contains Chinese.
- It **does** mean that opening one of the 166 raw call-log files may show the Chinese rendering that was produced for the author's own review. The English original is present elsewhere in the same record, or in the frozen inputs the record points at.
- The English-only conversion covered both the documentation layer and the derived-evidence layer, including fields that existed solely so the author could read a Chinese rendering of an already-English artefact. Those changes are **enumerated**, not silent: see the changelog below.

## How this is disclosed elsewhere

- `EVALS/EVALS_README.md` describes each evidence layer and what it can and cannot support.
- `EVALS/round3_dev_and_termination/v004/attempt1_preservation_baseline_v004.json` records the SHA-256 of every protected v003 file.
- `EVALS/round3_dev_and_termination/v004/englishization_changelog_v004.json` lists, file by file, every frozen artefact the English conversion touched — with its original hash, its new hash and the nature of the change — and is verified by `CODE/round3_v004/offline_validate_v004.py` (`englishization_changes_declared`, `v004_englishization_changes_declared`). No entry alters a number, a label, a measurement or an outcome.
- `CODE/verify_frozen_evidence.py --check` proves afterwards that all 5,370 evidence files still match their SHA-256 manifest, so the conversion cannot have gone further than the changelog says.
